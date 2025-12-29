import re
import textwrap
from pathlib import Path

LIST_NODE_DEF = """
// Definition for singly-linked list.
#[derive(PartialEq, Eq, Clone, Debug)]
pub struct ListNode {
    pub val: i32,
    pub next: Option<Box<ListNode>>
}

impl ListNode {
    #[inline]
    fn new(val: i32) -> Self {
        ListNode {
            next: None,
            val
        }
    }
}
"""

TREE_NODE_DEF = """
// Definition for a binary tree node.
use std::rc::Rc;
use std::cell::RefCell;

#[derive(Debug, PartialEq, Eq)]
pub struct TreeNode {
    pub val: i32,
    pub left: Option<Rc<RefCell<TreeNode>>>,
    pub right: Option<Rc<RefCell<TreeNode>>>,
}

impl TreeNode {
    #[inline]
    pub fn new(val: i32) -> Self {
        TreeNode {
            val,
            left: None,
            right: None
        }
    }
}
"""

class RustGenerator:
    def generate(self, folder_path: Path, core_code: str, meta: dict | None, overwrite: bool) -> str:
        filename = "solution.rs"
        out = folder_path / filename
        cmd = f"rustc {filename} && ./solution"

        if out.exists() and not overwrite:
            print(f"跳过 {filename}（已存在）")
            return cmd

        core_code = core_code or ""

        # 从 meta 提取方法名
        raw_fn_name = meta.get("name", "solve") if meta else "solve"
        fn_name = self._to_snake_case(raw_fn_name)

        # ✅ 核心改进：从 Rust 函数签名直接提取参数类型
        param_types = self._extract_param_types_from_signature(core_code, fn_name)
        ret_type_from_sig = self._extract_return_type_from_signature(core_code, fn_name)

        # 回退到 meta 信息
        if not param_types and meta:
            params = meta.get("params", [])
            param_types = [self._meta_type_to_rust(p.get("type", "integer")) for p in params]

        if not ret_type_from_sig and meta:
            ret_type_meta = (meta.get("return") or meta.get("ret") or {}).get("type", "integer")
            ret_type_from_sig = self._meta_type_to_rust(ret_type_meta)

        # 检测需要的数据结构
        has_list_node = "ListNode" in core_code
        has_tree_node = "TreeNode" in core_code

        code = self._build_full_code(core_code, fn_name, param_types, ret_type_from_sig, 
                                      has_list_node, has_tree_node)

        out.write_text(code, encoding="utf-8")
        print(f"生成 {filename}")
        return cmd

    def _to_snake_case(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _extract_param_types_from_signature(self, code: str, fn_name: str) -> list:
        """从 Rust 函数签名中提取参数类型"""
        # 匹配 pub fn fn_name(...) -> ... 的签名
        pattern = rf'pub\s+fn\s+{re.escape(fn_name)}\s*\((.*?)\)\s*->'
        match = re.search(pattern, code, re.DOTALL)
        if not match:
            return []

        params_str = match.group(1).strip()
        if not params_str:
            return []

        # 解析参数列表（简单版，处理常见情况）
        types = []
        for param in params_str.split(','):
            param = param.strip()
            if ':' in param:
                _, typ = param.split(':', 1)
                types.append(typ.strip())
        return types

    def _extract_return_type_from_signature(self, code: str, fn_name: str) -> str:
        """从 Rust 函数签名中提取返回类型"""
        pattern = rf'pub\s+fn\s+{re.escape(fn_name)}\s*\(.*?\)\s*->\s*([^\{{]+)'
        match = re.search(pattern, code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _meta_type_to_rust(self, meta_type: str) -> str:
        """将 LeetCode 元数据类型转换为 Rust 类型"""
        t = str(meta_type or "").strip().lower()
        if any(x in t for x in ["integer[]", "list", "vector"]):
            return "Vec<i32>"
        if "string" in t:
            return "String"
        if "listnode" in t:
            return "Option<Box<ListNode>>"
        if "treenode" in t:
            return "Option<Rc<RefCell<TreeNode>>>"
        return "i32"

    def _build_full_code(self, core_code: str, fn_name: str, param_types: list,
                         ret_type: str, has_list_node: bool, has_tree_node: bool) -> str:
        imports = """use std::fs;
"""
        if has_tree_node:
            imports += """use std::collections::VecDeque;
"""
        imports += "\n"

        defs = ""
        if has_list_node:
            defs += LIST_NODE_DEF + "\n"
        if has_tree_node:
            defs += TREE_NODE_DEF + "\n"

        core_code = self._extract_solution_body(core_code)
        helpers = self._helper_functions(has_list_node, has_tree_node)
        runner = self._runner_code(fn_name, param_types, ret_type)

        solution_impl = f"""
struct Solution;

impl Solution {{
{self._indent(core_code, 4)}
}}
"""
        return imports + defs + helpers + solution_impl + runner

    def _extract_solution_body(self, core_code: str) -> str:
        core_code = core_code.strip()
        impl_match = re.search(r'impl\s+Solution\s*\{([\s\S]*)\}\s*$', core_code)
        if impl_match:
            return textwrap.dedent(impl_match.group(1)).strip()
        return textwrap.dedent(core_code).strip()

    def _helper_functions(self, has_list_node: bool, has_tree_node: bool) -> str:
        helpers = """
// ============ 解析辅助函数 ============

fn parse_int(s: &str) -> i32 {
    s.trim().parse().unwrap_or(0)
}

fn parse_string(s: &str) -> String {
    let s = s.trim();
    if s.starts_with('"') && s.ends_with('"') {
        s[1..s.len()-1].to_string()
    } else {
        s.to_string()
    }
}

fn parse_int_array(s: &str) -> Vec<i32> {
    let s = s.trim();
    if s == "[]" || s.is_empty() { return vec![]; }
    let s = s.trim_start_matches('[').trim_end_matches(']');
    if s.is_empty() { return vec![]; }
    s.split(',')
        .map(|x| x.trim())
        .filter(|x| !x.is_empty())
        .map(|x| if x == "null" { i32::MIN } else { x.parse().unwrap_or(0) })
        .collect()
}
"""
        if has_list_node:
            helpers += """
fn parse_list_node(s: &str) -> Option<Box<ListNode>> {
    let vals = parse_int_array(s);
    if vals.is_empty() { return None; }
    let mut dummy = Box::new(ListNode::new(0));
    let mut cur = &mut dummy;
    for &val in &vals {
        if val != i32::MIN {
            cur.next = Some(Box::new(ListNode::new(val)));
            cur = cur.next.as_mut().unwrap();
        }
    }
    dummy.next
}

fn list_to_vec(head: Option<Box<ListNode>>) -> Vec<i32> {
    let mut result = vec![];
    let mut current = head;
    while let Some(node) = current {
        result.push(node.val);
        current = node.next;
    }
    result
}
"""
        if has_tree_node:
            helpers += """
fn parse_tree_node(s: &str) -> Option<Rc<RefCell<TreeNode>>> {
    let vals = parse_int_array(s);
    if vals.is_empty() || vals[0] == i32::MIN { return None; }
    let root = Rc::new(RefCell::new(TreeNode::new(vals[0])));
    let mut queue = VecDeque::new();
    queue.push_back(Rc::clone(&root));
    let mut i = 1;
    while !queue.is_empty() && i < vals.len() {
        if let Some(node) = queue.pop_front() {
            if i < vals.len() {
                if vals[i] != i32::MIN {
                    let left = Rc::new(RefCell::new(TreeNode::new(vals[i])));
                    node.borrow_mut().left = Some(Rc::clone(&left));
                    queue.push_back(left);
                }
                i += 1;
            }
            if i < vals.len() {
                if vals[i] != i32::MIN {
                    let right = Rc::new(RefCell::new(TreeNode::new(vals[i])));
                    node.borrow_mut().right = Some(Rc::clone(&right));
                    queue.push_back(right);
                }
                i += 1;
            }
        }
    }
    Some(root)
}

fn tree_to_vec(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<i32> {
    if root.is_none() { return vec![]; }
    let mut result = vec![];
    let mut queue = VecDeque::new();
    queue.push_back(root);
    while !queue.is_empty() {
        let node = queue.pop_front().unwrap();
        match node {
            None => result.push(i32::MIN),
            Some(n) => {
                result.push(n.borrow().val);
                queue.push_back(n.borrow().left.clone());
                queue.push_back(n.borrow().right.clone());
            }
        }
    }
    while result.last() == Some(&i32::MIN) { result.pop(); }
    result
}
"""
        return helpers

    def _runner_code(self, fn_name: str, param_types: list, ret_type: str) -> str:
        """根据从签名提取的精确类型生成 runner"""
        parse_steps = []
        call_args = []

        for i, rust_type in enumerate(param_types):
            var = f"arg{i}"
            rust_type = rust_type.replace(" ", "")  # 去除空格

            if "Option<Box<ListNode>>" in rust_type:
                parse_steps.append(f'        let {var} = parse_list_node(&inputs[{i}]);')
            elif "Option<Rc<RefCell<TreeNode>>>" in rust_type:
                parse_steps.append(f'        let {var} = parse_tree_node(&inputs[{i}]);')
            elif "Vec<i32>" in rust_type:
                parse_steps.append(f'        let {var} = parse_int_array(&inputs[{i}]);')
            elif "String" in rust_type:
                parse_steps.append(f'        let {var} = parse_string(&inputs[{i}]);')
            elif "i32" in rust_type or "i64" in rust_type:
                parse_steps.append(f'        let {var} = parse_int(&inputs[{i}]);')
            else:
                parse_steps.append(f'        let {var} = inputs[{i}].clone(); // Unknown type: {rust_type}')

            call_args.append(var)

        # 返回值处理
        ret_type = ret_type.replace(" ", "")
        if "Option<Box<ListNode>>" in ret_type:
            convert = "list_to_vec(got)"
            parse_exp = "let exp = parse_int_array(&expected);"
        elif "Option<Rc<RefCell<TreeNode>>>" in ret_type:
            convert = "tree_to_vec(got)"
            parse_exp = "let exp = parse_int_array(&expected);"
        elif "Vec<i32>" in ret_type:
            convert = "got"
            parse_exp = "let exp = parse_int_array(&expected);"
        elif "String" in ret_type:
            convert = "got"
            parse_exp = "let exp = parse_string(&expected);"
        elif "i32" in ret_type or "i64" in ret_type:
            convert = "got"
            parse_exp = "let exp = parse_int(&expected);"
        else:
            convert = "got"
            parse_exp = "let exp = expected.clone();"

        return f"""
fn main() {{
    let content = fs::read_to_string("testcases.txt").expect("testcases.txt not found");
    let blocks: Vec<&str> = content.split("\\n\\n").collect();
    let mut tc = 0;
    for block in blocks {{
        let block = block.trim();
        if block.is_empty() {{ continue; }}
        tc += 1;
        let mut inputs = Vec::new();
        let mut expected = String::new();
        let mut is_input = false;
        for line in block.lines() {{
            let line = line.trim();
            if line == "input:" {{ is_input = true; continue; }}
            if line.starts_with("output:") {{
                is_input = false;
                if line.len() > 7 {{
                    let inline = line[7..].trim();
                    if !inline.is_empty() {{ expected = inline.to_string(); }}
                }}
                continue;
            }}
            if is_input {{ inputs.push(line.to_string()); }}
            else if expected.is_empty() && !line.is_empty() {{ expected = line.to_string(); }}
        }}
        if inputs.len() < {len(param_types)} {{ continue; }}
        println!("Test {{}}:", tc);
        println!("  Input: {{:?}}", &inputs[..{len(param_types)}]);
{chr(10).join(parse_steps)}
        let got = Solution::{fn_name}({", ".join(call_args)});
        let got_display = {convert};
        println!("  Got: {{:?}}", got_display);
        if !expected.is_empty() {{
            {parse_exp}
            println!("  Exp: {{:?}}", exp);
            let got_str = format!("{{:?}}", got_display).replace(" ", "");
            let exp_str = format!("{{:?}}", exp).replace(" ", "");
            if got_str == exp_str {{ println!("  ✅ Passed"); }} else {{ println!("  ❌ Failed"); }}
        }} else {{ println!("  (No expected output)"); }}
        println!("--------------------");
    }}
}}
"""

    def _indent(self, text: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join(indent + line if line.strip() else "" for line in text.split("\n"))
