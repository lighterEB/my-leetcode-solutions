import re
import json
from pathlib import Path

LIST_NODE_DEF = """
// Definition for singly-linked list.
function ListNode(val, next) {
    this.val = (val===undefined ? 0 : val)
    this.next = (next===undefined ? null : next)
}
"""

TREE_NODE_DEF = """
// Definition for a binary tree node.
function TreeNode(val, left, right) {
    this.val = (val===undefined ? 0 : val)
    this.left = (left===undefined ? null : left)
    this.right = (right===undefined ? null : right)
}
"""

class JavaScriptGenerator:
    def generate(self, folder_path: Path, core_code: str, meta: dict | None, overwrite: bool) -> str:
        filename = "solution.js"
        out = folder_path / filename
        cmd = f"node {filename}"

        if out.exists() and not overwrite:
            print(f"跳过 {filename}（已存在）")
            return cmd

        core_code = core_code or ""

        # 提取元信息
        fn_name = meta.get("name", "solve") if meta else "solve"
        params = meta.get("params", []) if meta else []
        ret_type = (meta.get("return") or meta.get("ret") or {}).get("type", "integer") if meta else "integer"

        # ✅ 核心修复：不完全依赖 core_code 中的关键字，而是结合 meta 信息判断
        # 因为有时候 core_code 中只有参数名 l1, l2，没有显式的 ListNode 关键字
        has_list_node = re.search(r"\bListNode\b", core_code) is not None
        has_tree_node = re.search(r"\bTreeNode\b", core_code) is not None

        # 补充判断：如果参数类型里包含 ListNode/TreeNode，也必须开启
        for p in params:
            t_str = str(p.get("type", "")).lower()
            if "listnode" in t_str: has_list_node = True
            if "treenode" in t_str: has_tree_node = True

        # 生成完整代码
        code = self._build_full_code(core_code, fn_name, params, ret_type, has_list_node, has_tree_node)

        out.write_text(code, encoding="utf-8")
        print(f"生成 {filename}")
        return cmd

    def _build_full_code(self, core_code: str, fn_name: str, params: list, 
                         ret_type: str, has_list_node: bool, has_tree_node: bool) -> str:

        header = """const fs = require('fs');

"""
        defs = ""
        if has_list_node:
            defs += LIST_NODE_DEF + "\n"
        if has_tree_node:
            defs += TREE_NODE_DEF + "\n"

        helpers = self._helper_functions(has_list_node, has_tree_node)

        solution_part = f"""
// --- Solution Code ---
{core_code}

"""
        runner = self._runner_code(fn_name, params, ret_type)

        return header + defs + helpers + solution_part + runner

    def _helper_functions(self, has_list_node: bool, has_tree_node: bool) -> str:
        helpers = """
// --- Helpers ---
function parseValue(s) {
    if (!s) return null;
    try {
        return JSON.parse(s);
    } catch(e) {
        return s;
    }
}
"""
        if has_list_node:
            helpers += """
function buildList(arr) {
    if (!arr || !Array.isArray(arr) || !arr.length) return null;
    let head = new ListNode(arr[0]);
    let curr = head;
    for (let i = 1; i < arr.length; i++) {
        curr.next = new ListNode(arr[i]);
        curr = curr.next;
    }
    return head;
}

function listToArray(head) {
    if (Array.isArray(head)) return head; // Defense
    let res = [];
    while (head) {
        res.push(head.val);
        head = head.next;
    }
    return res;
}
"""
        if has_tree_node:
            helpers += """
function buildTree(arr) {
    if (!arr || !Array.isArray(arr) || !arr.length || arr[0] === null) return null;
    let root = new TreeNode(arr[0]);
    let queue = [root];
    let i = 1;
    while (queue.length && i < arr.length) {
        let node = queue.shift();
        if (i < arr.length && arr[i] !== null) {
            node.left = new TreeNode(arr[i]);
            queue.push(node.left);
        }
        i++;
        if (i < arr.length && arr[i] !== null) {
            node.right = new TreeNode(arr[i]);
            queue.push(node.right);
        }
        i++;
    }
    return root;
}

function treeToArray(root) {
    if (Array.isArray(root)) return root; // Defense
    if (!root) return [];
    let res = [];
    let queue = [root];
    while (queue.length) {
        let node = queue.shift();
        if (node) {
            res.push(node.val);
            queue.push(node.left);
            queue.push(node.right);
        } else {
            res.push(null);
        }
    }
    while (res.length && res[res.length - 1] === null) {
        res.pop();
    }
    return res;
}
"""
        return helpers

    def _runner_code(self, fn_name: str, params: list, ret_type: str) -> str:

        def norm_type(t: str) -> str:
            t = (t or "").strip().lower()
            if "listnode" in t: return "ListNode"
            if "treenode" in t: return "TreeNode"
            return "default"

        # 解析参数
        parse_args = []
        for i, p in enumerate(params):
            t = norm_type(p.get("type", ""))
            if t == "ListNode":
                parse_args.append(f"buildList(parseValue(inputs[{i}]))")
            elif t == "TreeNode":
                parse_args.append(f"buildTree(parseValue(inputs[{i}]))")
            else:
                parse_args.append(f"parseValue(inputs[{i}])")

        call_args = ", ".join(parse_args)

        # 返回值处理
        ret_norm = norm_type(ret_type)
        if ret_norm == "ListNode":
            convert_got = "listToArray(got)"
        elif ret_norm == "TreeNode":
            convert_got = "treeToArray(got)"
        else:
            convert_got = "got"

        return f"""
// --- Runner ---
function main() {{
    let content;
    try {{
        content = fs.readFileSync('testcases.txt', 'utf-8');
    }} catch (e) {{
        console.log("testcases.txt not found");
        return;
    }}

    let blocks = content.split('\\n\\n');
    let tc = 0;

    for (let block of blocks) {{
        block = block.trim();
        if (!block) continue;

        tc++;
        let lines = block.split('\\n');
        let inputs = [];
        let expected = null;
        let isInput = false;

        for (let line of lines) {{
            line = line.trim();
            if (line === 'input:') {{
                isInput = true;
                continue;
            }}
            if (line.startsWith('output:')) {{
                isInput = false;
                let inline = line.substring(7).trim();
                if (inline) expected = inline;
                continue;
            }}

            if (isInput) {{
                inputs.push(line);
            }} else if (expected === null && line) {{
                expected = line;
            }}
        }}

        if (inputs.length < {len(params)}) continue;

        console.log(`Test ${{tc}}:`);
        console.log("  Input:", inputs.slice(0, {len(params)}));

        try {{
            let got = {fn_name}({call_args});
            let gotDisplay = {convert_got};

            console.log("  Got:", JSON.stringify(gotDisplay));

            if (expected) {{
                let expObj = parseValue(expected);
                console.log("  Exp:", JSON.stringify(expObj));

                if (JSON.stringify(gotDisplay) === JSON.stringify(expObj)) {{
                    console.log("  ✅ Passed");
                }} else {{
                    console.log("  ❌ Failed");
                }}
            }} else {{
                console.log("  (No expected output)");
            }}
        }} catch (e) {{
            console.log("  Error:", e.message);
        }}
        console.log("--------------------");
    }}
}}

main();
"""
