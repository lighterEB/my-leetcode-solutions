import re
from pathlib import Path

# Go 数据结构定义
LIST_NODE_DEF = r"""
// Definition for singly-linked list.
type ListNode struct {
    Val  int
    Next *ListNode
}

func listFromSlice(vals []int) *ListNode {
    dummy := &ListNode{}
    cur := dummy
    for _, v := range vals {
        cur.Next = &ListNode{Val: v}
        cur = cur.Next
    }
    return dummy.Next
}

func listToSlice(head *ListNode) []int {
    res := []int{}
    for head != nil {
        res = append(res, head.Val)
        head = head.Next
    }
    return res
}
"""

TREE_NODE_DEF = r"""
// Definition for a binary tree node.
type TreeNode struct {
    Val   int
    Left  *TreeNode
    Right *TreeNode
}

// LeetCode 常用层序数组表示，例如 [1,2,3,null,4]
// Go 中用 []*int 表示（nil 代表 null）
func treeFromLevelOrder(vals []*int) *TreeNode {
    if len(vals) == 0 || vals[0] == nil {
        return nil
    }
    root := &TreeNode{Val: *vals[0]}
    q := []*TreeNode{root}
    i := 1
    for i < len(vals) && len(q) > 0 {
        node := q[0]
        q = q[1:]
        
        if i < len(vals) {
            if vals[i] != nil {
                node.Left = &TreeNode{Val: *vals[i]}
                q = append(q, node.Left)
            }
            i++
        }
        if i < len(vals) {
            if vals[i] != nil {
                node.Right = &TreeNode{Val: *vals[i]}
                q = append(q, node.Right)
            }
            i++
        }
    }
    return root
}

func treeToLevelOrder(root *TreeNode) []*int {
    if root == nil {
        return []*int{}
    }
    res := []*int{}
    q := []*TreeNode{root}
    for len(q) > 0 {
        node := q[0]
        q = q[1:]
        if node == nil {
            res = append(res, nil)
            continue
        }
        v := node.Val
        res = append(res, &v)
        q = append(q, node.Left, node.Right)
    }
    // 去掉末尾多余 nil
    for len(res) > 0 && res[len(res)-1] == nil {
        res = res[:len(res)-1]
    }
    return res
}
"""

class GoGenerator:
    def generate(self, folder_path: Path, core_code: str, meta: dict | None, overwrite: bool) -> str:
        filename = "solution.go"
        out = folder_path / filename
        cmd = f"go run {filename}"

        if out.exists() and not overwrite:
            print(f"跳过 {filename}（已存在）")
            return cmd

        core_code = core_code or ""

        # 检测需要注入的数据结构
        has_list_node = re.search(r"\bListNode\b", core_code) is not None
        has_tree_node = re.search(r"\bTreeNode\b", core_code) is not None

        defs = ""
        if has_list_node:
            defs += LIST_NODE_DEF + "\n"
        if has_tree_node:
            defs += TREE_NODE_DEF + "\n"

        # 提取元信息
        fn_name = meta.get("name", "solve") if meta else "solve"
        params = meta.get("params", []) if meta else []
        ret_type = (meta.get("return") or meta.get("ret") or {}).get("type", "integer") if meta else "integer"

        # 生成 runner
        runner = self._get_runner_code(fn_name, params, ret_type, has_list_node, has_tree_node)

        imports = """package main

import (
    "encoding/json"
    "fmt"
    "os"
    "strings"
)
"""
        
        full_code = imports + "\n" + defs + "\n" + core_code + "\n" + runner
        
        out.write_text(full_code, encoding="utf-8")
        print(f"生成 {filename}")
        return cmd

    def _get_runner_code(self, fn_name: str, params: list, ret_type: str, has_list_node: bool, has_tree_node: bool) -> str:
        # 构建参数解析逻辑
        parse_steps = []
        call_args = []

        for i, p in enumerate(params):
            t = p.get("type", "integer")
            var = f"arg{i}"
            
            if t == "integer":
                parse_steps.append(f"        var {var} int")
                parse_steps.append(f"        json.Unmarshal([]byte(lines[{i}]), &{var})")
            elif t == "integer[]":
                parse_steps.append(f"        var {var} []int")
                parse_steps.append(f"        json.Unmarshal([]byte(lines[{i}]), &{var})")
            elif t == "string":
                parse_steps.append(f"        var {var} string")
                parse_steps.append(f"        json.Unmarshal([]byte(lines[{i}]), &{var})")
            elif t == "ListNode":
                parse_steps.append(f"        var tmp{i} []int")
                parse_steps.append(f"        json.Unmarshal([]byte(lines[{i}]), &tmp{i})")
                parse_steps.append(f"        {var} := listFromSlice(tmp{i})")
            elif t == "TreeNode":
                parse_steps.append(f"        var tmp{i} []*int")
                parse_steps.append(f"        json.Unmarshal([]byte(lines[{i}]), &tmp{i})")
                parse_steps.append(f"        {var} := treeFromLevelOrder(tmp{i})")
            else:
                parse_steps.append(f"        var {var} any // TODO: parse {t}")
            
            call_args.append(var)

        call_args_str = ", ".join(call_args)

        # 根据返回类型生成对比逻辑
        if ret_type == "integer":
            exp_decl = "var exp int"
            got_show = "result"
            cmp = "result == exp"
        elif ret_type == "integer[]":
            exp_decl = "var exp []int"
            got_show = "result"
            cmp = "fmt.Sprint(result) == fmt.Sprint(exp)"
        elif ret_type == "string":
            exp_decl = "var exp string"
            got_show = "result"
            cmp = "result == exp"
        elif ret_type == "ListNode":
            exp_decl = "var exp []int"
            got_show = "listToSlice(result)"
            cmp = "fmt.Sprint(listToSlice(result)) == fmt.Sprint(exp)"
        elif ret_type == "TreeNode":
            exp_decl = "var exp []*int"
            got_show = "treeToLevelOrder(result)"
            cmp = "fmt.Sprint(treeToLevelOrder(result)) == fmt.Sprint(exp)"
        else:
            exp_decl = "var exp any"
            got_show = "result"
            cmp = "fmt.Sprint(result) == fmt.Sprint(exp)"

        return f"""
// --- Test Runner ---
func main() {{
    data, err := os.ReadFile("testcases.txt")
    if err != nil {{
        fmt.Println("testcases.txt not found")
        return
    }}
    content := strings.ReplaceAll(string(data), "\\r\\n", "\\n")
    blocks := strings.Split(content, "\\n\\n")

    tc := 0
    for _, block := range blocks {{
        block = strings.TrimSpace(block)
        if block == "" {{
            continue
        }}
        tc++

        raw := strings.Split(block, "\\n")
        lines := []string{{}}
        expected := ""
        inInput := false
        inOutput := false

        for _, ln := range raw {{
            ln = strings.TrimSpace(ln)
            if ln == "input:" {{
                inInput = true
                inOutput = false
                continue
            }}
            if ln == "output:" {{
                inInput = false
                inOutput = true
                continue
            }}

            if inInput {{
                lines = append(lines, ln)
            }} else if inOutput && expected == "" && ln != "" {{
                expected = ln
            }}
        }}

        if len(lines) < {len(params)} {{
            continue
        }}

        fmt.Printf("Test %d:\\n", tc)
        fmt.Printf("  Input: %v\\n", lines[:{len(params)}])

{chr(10).join(parse_steps)}

        result := {fn_name}({call_args_str})
        fmt.Printf("  Got: %v\\n", {got_show})

        if expected != "" {{
            {exp_decl}
            json.Unmarshal([]byte(expected), &exp)
            fmt.Printf("  Exp: %v\\n", exp)
            if {cmp} {{
                fmt.Println("  ✅ Passed")
            }} else {{
                fmt.Println("  ❌ Failed")
            }}
        }} else {{
            fmt.Println("  (No expected output)")
        }}
        fmt.Println("--------------------")
    }}
}}
"""
