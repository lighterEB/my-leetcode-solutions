import re
from pathlib import Path

# C++ 数据结构定义
LIST_NODE_DEF = r"""
// Definition for singly-linked list.
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

ListNode* listFromVector(const vector<int>& vals) {
    ListNode dummy(0);
    ListNode* curr = &dummy;
    for (int v : vals) {
        curr->next = new ListNode(v);
        curr = curr->next;
    }
    return dummy.next;
}

vector<int> listToVector(ListNode* head) {
    vector<int> res;
    while (head) {
        res.push_back(head->val);
        head = head->next;
    }
    return res;
}
"""

TREE_NODE_DEF = r"""
// Definition for a binary tree node.
struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

// LeetCode 层序表示：[1,2,3,null,4] -> 用 INT_MIN 表示 null
TreeNode* treeFromLevelOrder(const vector<int>& vals) {
    if (vals.empty() || vals[0] == INT_MIN) return nullptr;
    TreeNode* root = new TreeNode(vals[0]);
    queue<TreeNode*> q;
    q.push(root);
    int i = 1;
    while (i < vals.size() && !q.empty()) {
        TreeNode* node = q.front();
        q.pop();
        
        if (i < vals.size()) {
            if (vals[i] != INT_MIN) {
                node->left = new TreeNode(vals[i]);
                q.push(node->left);
            }
            i++;
        }
        if (i < vals.size()) {
            if (vals[i] != INT_MIN) {
                node->right = new TreeNode(vals[i]);
                q.push(node->right);
            }
            i++;
        }
    }
    return root;
}

vector<int> treeToLevelOrder(TreeNode* root) {
    vector<int> res;
    if (!root) return res;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* node = q.front();
        q.pop();
        if (!node) {
            res.push_back(INT_MIN);
            continue;
        }
        res.push_back(node->val);
        q.push(node->left);
        q.push(node->right);
    }
    // 去掉末尾的 INT_MIN
    while (!res.empty() && res.back() == INT_MIN) {
        res.pop_back();
    }
    return res;
}
"""

# 简单的 JSON 解析器（零依赖）
PARSER_CODE = r"""
// --- Simple Parser (zero dependency) ---
string trim(const string& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == string::npos) return "";
    size_t end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}

int parseInt(const string& s) {
    return stoi(trim(s));
}

string parseString(const string& s) {
    string t = trim(s);
    if (t.size() >= 2 && t[0] == '"' && t.back() == '"') {
        return t.substr(1, t.size() - 2);
    }
    return t;
}

vector<int> parseIntArray(const string& s) {
    string t = trim(s);
    vector<int> res;
    if (t == "[]") return res;
    if (t[0] == '[') t = t.substr(1);
    if (!t.empty() && t.back() == ']') t.pop_back();
    
    stringstream ss(t);
    string item;
    while (getline(ss, item, ',')) {
        string trimmed = trim(item);
        if (trimmed == "null") {
            res.push_back(INT_MIN); // 用 INT_MIN 表示 null
        } else {
            res.push_back(stoi(trimmed));
        }
    }
    return res;
}

template<typename T>
string vecToString(const vector<T>& v) {
    if (v.empty()) return "[]";
    stringstream ss;
    ss << "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i > 0) ss << ",";
        if (v[i] == INT_MIN) ss << "null";
        else ss << v[i];
    }
    ss << "]";
    return ss.str();
}
"""

class CppGenerator:
    def generate(self, folder_path: Path, core_code: str, meta: dict | None, overwrite: bool) -> str:
        filename = "solution.cpp"
        out = folder_path / filename
        cmd = f"g++ {filename} -std=c++17 -o solution && ./solution"

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

        # C++ 需要把 class Solution 的方法改成可调用的形式
        # LeetCode 的 C++ 代码通常是 class Solution { public: ... };
        # 我们保持原样即可

        
        includes = """#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <queue>
#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <climits>
#include <algorithm>
#include <functional>
using namespace std;

"""
        
        full_code = includes + defs + "\n" + PARSER_CODE + "\n" + core_code + "\n" + runner
        
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
                parse_steps.append(f"        int {var} = parseInt(lines[{i}]);")
            elif t == "integer[]" or t == "list<integer>":
                parse_steps.append(f"        vector<int> {var} = parseIntArray(lines[{i}]);")
            elif t == "string":
                parse_steps.append(f"        string {var} = parseString(lines[{i}]);")
            elif t == "ListNode":
                parse_steps.append(f"        ListNode* {var} = listFromVector(parseIntArray(lines[{i}]));")
            elif t == "TreeNode":
                parse_steps.append(f"        TreeNode* {var} = treeFromLevelOrder(parseIntArray(lines[{i}]));")
            else:
                parse_steps.append(f"        // TODO: parse {t}")
            
            call_args.append(var)

        call_args_str = ", ".join(call_args)

        # 根据返回类型生成对比逻辑
        if ret_type == "integer":
            exp_decl = "int exp = parseInt(expected);"
            got_show = "to_string(result)"
            cmp = "result == exp"
            exp_show = "to_string(exp)"
        elif ret_type == "integer[]" or ret_type == "list<integer>":
            exp_decl = "vector<int> exp = parseIntArray(expected);"
            got_show = "vecToString(result)"
            cmp = "result == exp"
            exp_show = "vecToString(exp)"
        elif ret_type == "string":
            exp_decl = "string exp = parseString(expected);"
            got_show = "result"
            cmp = "result == exp"
            exp_show = "exp"
        elif ret_type == "ListNode":
            exp_decl = "vector<int> exp = parseIntArray(expected);"
            got_show = "vecToString(listToVector(result))"
            cmp = "listToVector(result) == exp"
            exp_show = "vecToString(exp)"
        elif ret_type == "TreeNode":
            exp_decl = "vector<int> exp = parseIntArray(expected);"
            got_show = "vecToString(treeToLevelOrder(result))"
            cmp = "treeToLevelOrder(result) == exp"
            exp_show = "vecToString(exp)"
        else:
            exp_decl = f"string exp = expected; /* Unknown type: {ret_type} */"
            got_show = "\"(unknown type)\""
            cmp = "false"
            exp_show = "exp"

        return f"""
// --- Test Runner ---
int main() {{
    ifstream file("testcases.txt");
    if (!file.is_open()) {{
        cout << "testcases.txt not found" << endl;
        return 0;
    }}

    stringstream buffer;
    buffer << file.rdbuf();
    string content = buffer.str();
    file.close();

    // 按空行分割 blocks
    vector<string> blocks;
    stringstream ss(content);
    string line;
    string block;
    while (getline(ss, line)) {{
        if (line.empty() || line == "\\r") {{
            if (!block.empty()) {{
                blocks.push_back(block);
                block.clear();
            }}
        }} else {{
            block += line + "\\n";
        }}
    }}
    if (!block.empty()) blocks.push_back(block);

    Solution sol;
    int tc = 0;

    for (const auto& blk : blocks) {{
        tc++;
        
        vector<string> lines;
        string expected;
        bool inInput = false, inOutput = false;

        stringstream ss2(blk);
        string ln;
        while (getline(ss2, ln)) {{
            ln = trim(ln);
            if (ln == "input:") {{
                inInput = true;
                inOutput = false;
                continue;
            }}
            if (ln == "output:") {{
                inInput = false;
                inOutput = true;
                continue;
            }}

            if (inInput) {{
                lines.push_back(ln);
            }} else if (inOutput && expected.empty() && !ln.empty()) {{
                expected = ln;
            }}
        }}

        if (lines.size() < {len(params)}) continue;

        cout << "Test " << tc << ":" << endl;
        cout << "  Input: [";
        for (int i = 0; i < {len(params)}; i++) {{
            if (i > 0) cout << ", ";
            cout << lines[i];
        }}
        cout << "]" << endl;

{chr(10).join(parse_steps)}

        auto result = sol.{fn_name}({call_args_str});
        cout << "  Got: " << {got_show} << endl;

        if (!expected.empty()) {{
            {exp_decl}
            cout << "  Exp: " << {exp_show} << endl;
            if ({cmp}) {{
                cout << "  ✅ Passed" << endl;
            }} else {{
                cout << "  ❌ Failed" << endl;
            }}
        }} else {{
            cout << "  (No expected output)" << endl;
        }}
        cout << "--------------------" << endl;
    }}

    return 0;
}}
"""

