import re
from pathlib import Path

LIST_NODE_DEF = """
    // Definition for singly-linked list.
    static class ListNode {
        int val;
        ListNode next;
        ListNode() {}
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }
"""

TREE_NODE_DEF = """
    // Definition for a binary tree node.
    static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode() {}
        TreeNode(int val) { this.val = val; }
        TreeNode(int val, TreeNode left, TreeNode right) {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }
"""

class JavaGenerator:
    def generate(self, folder_path: Path, core_code: str, meta: dict | None, overwrite: bool) -> str:
        filename = "Solution.java"
        out = folder_path / filename
        cmd = f"java {filename}"

        if out.exists() and not overwrite:
            print(f"跳过 {filename}（已存在）")
            return cmd

        core_code = core_code or ""

        # 检测需要的数据结构
        has_list_node = re.search(r"\bListNode\b", core_code) is not None
        has_tree_node = re.search(r"\bTreeNode\b", core_code) is not None

        # 提取元信息
        fn_name = meta.get("name", "solve") if meta else "solve"
        params = meta.get("params", []) if meta else []
        ret_type = (meta.get("return") or meta.get("ret") or {}).get("type", "integer") if meta else "integer"

        # 确保是 public class
        core_code = re.sub(r"\bclass\s+Solution\b", "public class Solution", core_code)

        # 生成内部定义和工具
        inner = self._inner_helpers(has_list_node, has_tree_node)
        
        # 生成 runner
        runner = self._runner_code(fn_name, params, ret_type)

        # 插入到 Solution 类里
        m = re.search(r"(public\s+class\s+Solution\s*\{)", core_code)
        if m:
            insert_pos = m.end()
            core_code = core_code[:insert_pos] + "\n" + inner + "\n" + core_code[insert_pos:]

        # 在类末尾加 runner
        r_idx = core_code.rfind("}")
        if r_idx != -1:
            core_code = core_code[:r_idx] + "\n" + runner + "\n" + core_code[r_idx:]
        else:
            core_code = core_code + "\n" + runner

        imports = "import java.util.*;\nimport java.io.*;\n\n"
        out.write_text(imports + core_code, encoding="utf-8")
        print(f"生成 {filename}")
        return cmd

    def _inner_helpers(self, has_list_node: bool, has_tree_node: bool) -> str:
        defs = ""
        if has_list_node:
            defs += LIST_NODE_DEF + "\n"
        if has_tree_node:
            defs += TREE_NODE_DEF + "\n"

        helpers = """
    // --- 简单解析器（零依赖）---
    private static int parseIntScalar(String s) {
        return Integer.parseInt(s.trim());
    }

    private static String parseString(String s) {
        s = s.trim();
        if (s.length() >= 2 && s.startsWith("\\"") && s.endsWith("\\"")) {
            return s.substring(1, s.length() - 1);
        }
        return s;
    }

    private static int[] parseIntArray(String s) {
        s = s.trim();
        if (s.equals("[]")) return new int[0];
        if (s.startsWith("[")) s = s.substring(1);
        if (s.endsWith("]")) s = s.substring(0, s.length() - 1);
        if (s.trim().isEmpty()) return new int[0];
        
        String[] parts = s.split(",");
        int[] res = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            String part = parts[i].trim();
            if (part.equals("null")) {
                res[i] = Integer.MIN_VALUE;
            } else {
                res[i] = Integer.parseInt(part);
            }
        }
        return res;
    }
"""

        if has_list_node:
            helpers += """
    private static ListNode parseListNode(String s) {
        int[] vals = parseIntArray(s);
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        for (int v : vals) {
            if (v != Integer.MIN_VALUE) {
                cur.next = new ListNode(v);
                cur = cur.next;
            }
        }
        return dummy.next;
    }

    private static int[] listNodeToArray(ListNode head) {
        List<Integer> tmp = new ArrayList<>();
        while (head != null) {
            tmp.add(head.val);
            head = head.next;
        }
        int[] res = new int[tmp.size()];
        for (int i = 0; i < tmp.size(); i++) res[i] = tmp.get(i);
        return res;
    }
"""

        if has_tree_node:
            helpers += """
    private static TreeNode parseTreeNode(String s) {
        int[] vals = parseIntArray(s);
        if (vals.length == 0 || vals[0] == Integer.MIN_VALUE) return null;
        
        TreeNode root = new TreeNode(vals[0]);
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        int i = 1;
        
        while (!q.isEmpty() && i < vals.length) {
            TreeNode node = q.poll();
            
            if (i < vals.length) {
                if (vals[i] != Integer.MIN_VALUE) {
                    node.left = new TreeNode(vals[i]);
                    q.offer(node.left);
                }
                i++;
            }
            
            if (i < vals.length) {
                if (vals[i] != Integer.MIN_VALUE) {
                    node.right = new TreeNode(vals[i]);
                    q.offer(node.right);
                }
                i++;
            }
        }
        return root;
    }

    private static int[] treeToArray(TreeNode root) {
        if (root == null) return new int[0];
        List<Integer> res = new ArrayList<>();
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            if (node == null) {
                res.add(Integer.MIN_VALUE);
                continue;
            }
            res.add(node.val);
            q.offer(node.left);
            q.offer(node.right);
        }
        
        while (!res.isEmpty() && res.get(res.size() - 1) == Integer.MIN_VALUE) {
            res.remove(res.size() - 1);
        }
        
        int[] arr = new int[res.size()];
        for (int i = 0; i < res.size(); i++) arr[i] = res.get(i);
        return arr;
    }
"""

        helpers += """
    private static String show(Object x) {
        if (x == null) return "null";
        if (x instanceof int[]) return Arrays.toString((int[]) x);
        if (x instanceof List) return ((List<?>) x).toString();
        return x.toString();
    }
"""

        return defs + helpers

    def _runner_code(self, fn_name: str, params: list, ret_type: str) -> str:
        # 规范化类型（兼容各种写法）
        def norm_type(t: str) -> str:
            t = (t or "").strip()
            if t in ["integer[]", "list<integer>", "List<Integer>"]:
                return "int[]"
            if t == "integer":
                return "int"
            return t

        # 参数解析
        parse_steps = []
        call_args = []

        for i, p in enumerate(params):
            t = norm_type(p.get("type", "integer"))
            var = f"arg{i}"
            
            if t == "int":
                parse_steps.append(f"                int {var} = parseIntScalar(inputs.get({i}));")
            elif t == "int[]":
                parse_steps.append(f"                int[] {var} = parseIntArray(inputs.get({i}));")
            elif t == "string":
                parse_steps.append(f"                String {var} = parseString(inputs.get({i}));")
            elif t == "ListNode":
                parse_steps.append(f"                ListNode {var} = parseListNode(inputs.get({i}));")
            elif t == "TreeNode":
                parse_steps.append(f"                TreeNode {var} = parseTreeNode(inputs.get({i}));")
            else:
                parse_steps.append(f"                Object {var} = null; // TODO: {t}")
            
            call_args.append(var)

        # 返回值处理（统一转成便于比对的格式）
        ret_norm = norm_type(ret_type)
        
        if ret_norm == "ListNode":
            convert = "listNodeToArray((ListNode) got)"
            parse_exp = "int[] exp = parseIntArray(expected);"
        elif ret_norm == "TreeNode":
            convert = "treeToArray((TreeNode) got)"
            parse_exp = "int[] exp = parseIntArray(expected);"
        elif ret_norm == "int[]":
            convert = "got"
            parse_exp = "int[] exp = parseIntArray(expected);"
        elif ret_norm == "int":
            convert = "got"
            parse_exp = "int exp = parseIntScalar(expected);"
        elif ret_norm == "string":
            convert = "got"
            parse_exp = "String exp = parseString(expected);"
        else:
            # 通用兜底
            convert = "got"
            parse_exp = "Object exp = expected;"

        return f"""
    public static void main(String[] args) throws Exception {{
        File f = new File("testcases.txt");
        if (!f.exists()) {{
            System.out.println("testcases.txt not found");
            return;
        }}

        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new FileReader(f))) {{
            String line;
            while ((line = br.readLine()) != null) {{
                sb.append(line).append("\\n");
            }}
        }}
        String content = sb.toString().replace("\\r\\n", "\\n");
        String[] blocks = content.split("\\n\\n");

        int tc = 0;
        for (String block : blocks) {{
            block = block.trim();
            if (block.isEmpty()) continue;
            tc++;

            List<String> inputs = new ArrayList<>();
            String expected = null;
            boolean isInput = false;

            for (String ln : block.split("\\n")) {{
                ln = ln.trim();
                
                if (ln.equals("input:")) {{
                    isInput = true;
                    continue;
                }}
                
                if (ln.equals("output:") || ln.startsWith("output:")) {{
                    isInput = false;
                    if (ln.length() > 7) {{
                        String inline = ln.substring(7).trim();
                        if (!inline.isEmpty()) expected = inline;
                    }}
                    continue;
                }}

                if (isInput) {{
                    inputs.add(ln);
                }} else if (expected == null && !ln.isEmpty()) {{
                    expected = ln;
                }}
            }}

            if (inputs.size() < {len(params)}) continue;

            System.out.println("Test " + tc + ":");
            System.out.println("  Input: " + inputs.subList(0, {len(params)}));

            try {{
{chr(10).join(parse_steps)}

                Solution sol = new Solution();
                Object got = sol.{fn_name}({", ".join(call_args)});
                Object gotDisplay = {convert};

                System.out.println("  Got: " + show(gotDisplay));

                if (expected != null) {{
                    {parse_exp}
                    System.out.println("  Exp: " + show(exp));
                    
                    // 字符串级对比（去空格，最健壮）
                    String gotStr = show(gotDisplay).replace(" ", "");
                    String expStr = show(exp).replace(" ", "");
                    boolean passed = gotStr.equals(expStr);
                    
                    System.out.println(passed ? "  ✅ Passed" : "  ❌ Failed");
                }} else {{
                    System.out.println("  (No expected output)");
                }}
            }} catch (Exception e) {{
                System.out.println("  Error: " + e.getMessage());
                e.printStackTrace();
            }}
            System.out.println("--------------------");
        }}
    }}
"""
