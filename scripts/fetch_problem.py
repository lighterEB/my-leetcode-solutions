#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import json
import argparse
from pathlib import Path

import requests
import html2text  # pip install html2text [web:437]

from generators.registry import get_generator

API_URL = "https://leetcode.cn/graphql/"
HEADERS = {"Content-Type": "application/json"}

LANG_CONFIG = {
    "python": {"ext": "py", "langSlug": "python3"},
    "java":   {"ext": "java", "langSlug": "java"}, 
    "rust":   {"ext": "rust", "langSlug": "rust"},
    "go":   {"ext": "go", "langSlug": "golang"},
    "cpp":   {"ext": "cpp", "langSlug": "cpp"},


}

def html_to_markdown(html: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0
    return h.handle(html or "").strip()


def resolve_title_slug(slug_or_id: str) -> str:
    s = (slug_or_id or "").strip()
    if not s:
        raise ValueError("empty slug_or_id")

    # 如果是非数字，说明已经是 slug，直接返回
    if not s.isdigit():
        return s

    qid = s # 目标题号，如 "1"

    # --- 核心修改：使用 CN 站最稳的 REST API ---
    # 相比 GraphQL 各种字段报错，CN 站保留的这个旧版 API 是最无敌的。
    # 它不需要 cookie 也能返回全量题库的 id -> slug 映射。
    # API 地址: https://leetcode.cn/api/problems/all/
    
    try:
        # 注意：这里我们临时切到 REST API，因为它比 CN 的 GraphQL 稳太多了
        # 且返回速度非常快 (gzip 后很小)
        api_url = "https://leetcode.cn/api/problems/all/"
        resp = requests.get(api_url, headers=HEADERS, timeout=15)
        
        if resp.status_code != 200:
            print(f"REST API 失败 (HTTP {resp.status_code})，尝试 GraphQL...")
            raise Exception("REST API failed") # 抛出异常去走下面的 GraphQL 备选（如果有的话）

        data = resp.json()
        
        # 解析 REST API 返回结构
        # 结构: {"stat_status_pairs": [ {"stat": {"frontend_question_id": "1", "question__title_slug": "two-sum", ...} }, ... ]}
        pairs = data.get("stat_status_pairs", [])
        
        for pair in pairs:
            stat = pair.get("stat", {})
            # 注意：CN 站 API 返回的 frontend_question_id 可能是 int 也可能是 str
            # 必须转 str 对比
            curr_id = str(stat.get("frontend_question_id"))
            if curr_id == qid:
                return stat.get("question__title_slug")
                
        raise RuntimeError(f"在全量题库中未找到题号 {qid} (REST API)")

    except Exception as e:
        print(f"Plan A (REST API) 出错: {e}，尝试 Plan B (GraphQL)...")
        
        # --- Plan B: GraphQL (针对 CN 站修正版) ---
        # 如果 REST API 挂了，用这个极简的 GraphQL
        # 注意：CN 站字段往往是 questionFrontendId (驼峰) 但不在 ProblemSet 节点下
        # 这里尝试 standard global query
        
        query = """
        query getQuestionList {
            allQuestions {
                questionFrontendId
                titleSlug
            }
        }
        """
        
        # 这里的 API_URL 必须是 https://leetcode.cn/graphql/
        payload = {
            "query": query,
            "operationName": "getQuestionList"
        }
        
        resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
             resp.raise_for_status()
             
        j = resp.json()
        if "errors" in j:
             raise RuntimeError(f"GraphQL 报错: {j['errors']}")
             
        qs = j.get("data", {}).get("allQuestions", [])
        for item in qs:
            if str(item.get("questionFrontendId")) == qid:
                return item["titleSlug"]
                
        raise RuntimeError(f"未找到题号 {qid} (Plan B)")

def get_problem_data(title_slug: str) -> dict:
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        title
        titleSlug
        difficulty
        content
        exampleTestcaseList
        metaData
        codeSnippets {
          langSlug
          code
        }
      }
    }
    """
    payload = {"query": query, "variables": {"titleSlug": title_slug}}
    resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    q = resp.json()["data"]["question"]
    if not q:
        print("题目未找到，请检查 slug 是否正确")
        sys.exit(1)
    return q

def clean_md_prefix(s: str) -> str:
    s = (s or "").replace("\u00a0", " ").strip()
    # 去掉行首的若干 *（如 ** 或 *）以及其后的空白
    s = re.sub(r"^\*+\s*", "", s)
    # 再保险：去掉可能残留的行首空白
    return s.lstrip()

def extract_outputs_from_html(content_html: str) -> list[str]:
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.body_width = 0
    text = h.handle(content_html or "")

    lines = [ln.strip() for ln in text.splitlines()]
    outs = []

    # 允许：Output / **Output** / 输出；允许有无冒号；允许冒号是 : 或 ：
    pat = re.compile(r"^\*{0,2}(Output|输出)\*{0,2}\s*[:：]?\s*(.*)$", re.IGNORECASE)

    i = 0
    while i < len(lines):
        m = pat.match(lines[i])
        if not m:
            i += 1
            continue

        # 情况1：同一行就带值
        tail = clean_md_prefix(m.group(2))
        if tail:
            outs.append(tail)
            i += 1
            continue

        # 情况2：值在后续若干行（跳过空行）
        j = i + 1
        while j < len(lines) and lines[j] == "":
            j += 1
        if j < len(lines):
            # 防止把 Explanation 当成 Output
            if not re.match(r"^\*{0,2}(Explanation|解释)\*{0,2}\s*[:：]?", lines[j], re.IGNORECASE):
                val = clean_md_prefix(lines[j])
                if val:
                    outs.append(val)
                    i = j + 1
                    continue

        i += 1

    return outs

def write_problem_md(folder: Path, data: dict) -> None:
    slug = data["titleSlug"]
    content_md = html_to_markdown(data.get("content", ""))

    md = (
        f"# {data['questionId']}. {data['title']}\n\n"
        f"难度：{data['difficulty']}\n\n"
        f"链接：https://leetcode.cn/problems/{slug}/\n\n"
        f"## 题目描述\n\n"
        f"{content_md}\n"
    )
    (folder / "problem.md").write_text(md, encoding="utf-8")

def write_testcases_txt(folder: Path, example_list: list[str], content_html: str) -> None:
    outs = extract_outputs_from_html(content_html)
    p = folder / "testcases.txt"

    buf = ""
    for i, ex in enumerate(example_list, 1):
        buf += f"input:\n{ex.strip()}\n"
        if i <= len(outs):
            buf += f"output:\n{outs[i-1]}\n"
        else:
            buf += "output:\n\n"
        buf += "\n"

    p.write_text(buf, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="LeetCode 拉题：主程序 + 生成器拆分版（先支持 Python）")
    parser.add_argument("slug", help="题目 slug（如 two-sum）或题号(1)")
    parser.add_argument("-l", "--langs", default="python", help="语言列表（逗号分隔），目前先支持 python")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的 solution 文件")
    args = parser.parse_args()

    title_slug = resolve_title_slug(args.slug)
    data = get_problem_data(title_slug)

    qid = str(data["questionId"]).zfill(4)
    folder = Path(f"{qid}-{data['titleSlug']}")
    folder.mkdir(exist_ok=True)

    write_problem_md(folder, data)
    write_testcases_txt(folder, data.get("exampleTestcaseList") or [], data.get("content") or "")

    # metaData（用于通用 runner）
    meta = None
    if data.get("metaData"):
        try:
            meta = json.loads(data["metaData"])
        except Exception:
            meta = None

    snippets = {s["langSlug"]: s["code"] for s in (data.get("codeSnippets") or []) if s.get("langSlug")}
    
    # 解析用户输入的语言列表
    target_langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    
    # 用于收集各语言的启动命令
    run_commands = []

    for lang in target_langs:
        if lang not in LANG_CONFIG:
            print(f"⚠️  跳过 {lang}：尚未注册生成器 (registry.py)")
            continue
            
        config = LANG_CONFIG[lang]
        # 获取该语言的题目原始代码
        core = snippets.get(config["langSlug"], "") or ""
        
        # 获取生成器实例
        gen = get_generator(lang)
        
        # --- 关键修改：接收生成器返回的运行命令 ---
        # 假设 generate 现在的签名是 -> str
        cmd = gen.generate(folder_path=folder, core_code=core, meta=meta, overwrite=args.overwrite)
        
        if cmd:
            run_commands.append((lang, cmd))

    print(f"完成：{folder}")

    # --- 统一打印所有语言的单文件执行命令 ---
    if run_commands:
        print("\n" + "="*60)
        print(f"✅ 题目已就绪：{folder.absolute()}")
        print("="*60)
        print("🚀 快速开始 ")
        print(f"  cd {folder.name}")
        print("-" * 30)
        
        # 动态计算对齐宽度，让输出更整齐
        max_lang_len = max(len(l) for l, _ in run_commands)
        
        for lang, cmd in run_commands:
            # 格式化输出，例如: [python] python3 solution.py
            lang_label = f"👉{lang}:".ljust(max_lang_len + 3)
            print(f"  {lang_label} {cmd}")
            
        print("="*60 + "\n")

if __name__ == "__main__":
    main()

