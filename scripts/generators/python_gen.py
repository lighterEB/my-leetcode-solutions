import re
from pathlib import Path

LIST_NODE_DEF = """
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
"""

TREE_NODE_DEF = """
# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
"""

class PythonGenerator:
    def generate(self, folder_path: Path, core_code: str, meta: dict | None, overwrite: bool) -> str:
        filename = "solution.py"
        out = folder_path / filename
        cmd = f"python3 {filename}"

        if out.exists() and not overwrite:
            print(f"跳过 {filename}（已存在）")
            return cmd

        core_code = core_code or ""

        has_list_node = re.search(r"\bListNode\b", core_code) is not None
        has_tree_node = re.search(r"\bTreeNode\b", core_code) is not None

        fn_name = meta.get("name", "solve") if meta else "solve"
        params = meta.get("params", []) if meta else []
        ret_type_from_sig = self._extract_return_type_from_signature(core_code, fn_name)

        code = self._build_full_code(core_code, fn_name, params, ret_type_from_sig, 
                                      has_list_node, has_tree_node)

        out.write_text(code, encoding="utf-8")
        print(f"生成 {filename}")
        return cmd

    def _extract_return_type_from_signature(self, code: str, fn_name: str) -> str:
        pattern = rf'def\s+{re.escape(fn_name)}\s*\([^)]*\)\s*->\s*([^:]+):'
        match = re.search(pattern, code)
        if match:
            return match.group(1).strip()
        return "int"

    def _build_full_code(self, core_code: str, fn_name: str, params: list, 
                         ret_type: str, has_list_node: bool, has_tree_node: bool) -> str:
        imports = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, List
from collections import deque

"""

        defs = ""
        if has_list_node:
            defs += LIST_NODE_DEF + "\n"
        if has_tree_node:
            defs += TREE_NODE_DEF + "\n"

        core_code = self._extract_solution_body(core_code)
        helpers = self._helper_functions(has_list_node, has_tree_node)
        runner = self._runner_code(fn_name, params, ret_type)

        solution_impl = f"""
class Solution:
{self._indent(core_code, 4)}
"""
        return imports + defs + helpers + solution_impl + runner

    def _extract_solution_body(self, core_code: str) -> str:
        core_code = core_code.strip()
        match = re.search(r'class\s+Solution.*?:\s*(.*)', core_code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return core_code

    def _helper_functions(self, has_list_node: bool, has_tree_node: bool) -> str:
        helpers = """
# ============ 解析辅助函数 ============

def parse_value(s):
    \"\"\"通用解析函数，支持 int, list, string 等\"\"\"
    s = s.strip()
    if s == "null":
        return None

    # ✅ 核心修复：处理 JSON 格式的 null/true/false
    if "null" in s or "true" in s or "false" in s:
        s = s.replace("null", "None").replace("true", "True").replace("false", "False")

    try:
        return eval(s)
    except:
        return s
"""

        if has_list_node:
            helpers += """
def build_list(vals):
    if not vals: return None
    if not isinstance(vals, list): return ListNode(vals) # Fallback
    dummy = ListNode(0)
    curr = dummy
    for val in vals:
        if val is not None:
            curr.next = ListNode(val)
            curr = curr.next
    return dummy.next

def list_to_array(head):
    if isinstance(head, list): return head
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result
"""

        if has_tree_node:
            helpers += """
def build_tree(vals):
    if not vals or vals[0] is None: return None
    if not isinstance(vals, list): return TreeNode(vals) # Fallback

    root = TreeNode(vals[0])
    queue = deque([root])
    i = 1

    while queue and i < len(vals):
        node = queue.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root

def tree_to_array(root):
    if isinstance(root, list): return root
    if not root: return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    while result and result[-1] is None: result.pop()
    return result
"""
        return helpers

    def _runner_code(self, fn_name: str, params: list, ret_type: str) -> str:
        def norm_param_type(t: str) -> str:
            t = (t or "").strip().lower()
            if "listnode" in t: return "ListNode"
            if "treenode" in t: return "TreeNode"
            return "default"

        def norm_return_type(t: str) -> str:
            t = str(t).strip()
            if "List[" in t: return "default"
            if "ListNode" in t: return "ListNode"
            if "TreeNode" in t: return "TreeNode"
            return "default"

        parse_steps = []
        call_args = []
        for i, p in enumerate(params):
            t = norm_param_type(p.get("type", "integer"))
            var = f"arg{i}"
            if t == "ListNode":
                parse_steps.append(f"            {var} = build_list(parse_value(inputs[{i}]))")
            elif t == "TreeNode":
                parse_steps.append(f"            {var} = build_tree(parse_value(inputs[{i}]))")
            else:
                parse_steps.append(f"            {var} = parse_value(inputs[{i}])")
            call_args.append(var)

        ret_norm = norm_return_type(ret_type)
        if ret_norm == "ListNode": convert = "list_to_array(got)"
        elif ret_norm == "TreeNode": convert = "tree_to_array(got)"
        else: convert = "got"

        parse_lines = "\n".join(parse_steps) if parse_steps else "            pass"

        return f"""
def main():
    try:
        with open("testcases.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("testcases.txt not found")
        return

    blocks = content.strip().split("\\n\\n")
    tc = 0
    for block in blocks:
        block = block.strip()
        if not block: continue
        tc += 1
        inputs = []
        expected = None
        is_input = False
        for line in block.split("\\n"):
            line = line.strip()
            if line == "input:": is_input = True; continue
            if line.startswith("output:"):
                is_input = False
                inline = line[7:].strip()
                if inline: expected = inline
                continue
            if is_input: inputs.append(line)
            elif expected is None and line: expected = line

        if len(inputs) < {len(params)}: continue
        print(f"Test {{tc}}:")
        print(f"  Input: {{inputs[:{len(params)}]}}")
        try:
{parse_lines}
            solution = Solution()
            got = solution.{fn_name}({", ".join(call_args)})
            got_display = {convert}
            print(f"  Got: {{got_display}}")
            if expected:
                exp = parse_value(expected)
                print(f"  Exp: {{exp}}")
                got_str = str(got_display).replace(" ", "")
                exp_str = str(exp).replace(" ", "")
                if got_str == exp_str: print("  ✅ Passed")
                else: print("  ❌ Failed")
            else: print("  (No expected output)")
        except Exception as e:
            print(f"  Error: {{e}}")
            import traceback
            traceback.print_exc()
        print("-" * 20)

if __name__ == "__main__":
    main()
"""

    def _indent(self, text: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join(indent + line if line.strip() else "" for line in text.split("\n"))
