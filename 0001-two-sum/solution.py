
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:

# ---- Local Test Runner (auto-generated) ----
import json
import sys
from pathlib import Path

__META__ = json.loads('{"name": "twoSum", "params": [{"name": "nums", "type": "integer[]"}, {"name": "target", "type": "integer"}], "return": {"type": "integer[]", "size": 2}, "manual": false}')

# --- Helpers for Data Structures ---

def _list_to_link(vals):
    if not vals: return None
    head = ListNode(vals[0])
    curr = head
    for x in vals[1:]:
        curr.next = ListNode(x)
        curr = curr.next
    return head

def _link_to_list(node):
    res = []
    while node:
        res.append(node.val)
        node = node.next
    return res

def _list_to_tree(vals):
    if not vals: return None
    nodes = [TreeNode(v) if v is not None else None for v in vals]
    kids = nodes[::-1]
    root = kids.pop()
    for node in nodes:
        if node:
            if kids: node.left = kids.pop()
            if kids: node.right = kids.pop()
    return root

def _tree_to_list(root):
    # 简化的层序遍历输出，用于对比结果
    if not root: return []
    res = []
    q = [root]
    while q:
        node = q.pop(0)
        if node:
            res.append(node.val)
            q.append(node.left)
            q.append(node.right)
        else:
            res.append(None)
    # 去掉末尾多余的 None
    while res and res[-1] is None:
        res.pop()
    return res

# --- Parser ---

def _parse_scalar(base: str, s: str):
    t = s.strip()
    if base in ("integer", "long"): return int(t)
    if base == "double": return float(t)
    if base == "boolean": return t.lower() in ("true", "1")
    if base == "string":
        if len(t) >= 2 and ((t[0] == '"' and t[-1] == '"') or (t[0] == "'" and t[-1] == "'")):
            return t[1:-1]
        return t
    raise ValueError("unsupported base: " + base)

def _parse_value(ts: dict, s: str):
    # 处理复杂类型
    typ = ts.get("type", "")
    
    # 1. 链表 (ListNode)
    if typ == "ListNode":
        vals = json.loads(s) # 输入通常是 JSON 数组 [1,2,3]
        return _list_to_link(vals)
        
    # 2. 二叉树 (TreeNode)
    if typ == "TreeNode":
        vals = json.loads(s) # 输入通常是 JSON 数组 [1,null,2,3]
        return _list_to_tree(vals)
    
    # 3. 数组/矩阵
    base = typ.replace("[]", "")
    dims = typ.count("[]")
    
    # 如果明确是 list<ListNode> 这种嵌套结构（较少见），需要递归处理
    # 这里处理最通用的基础类型数组
    if dims > 0:
        return json.loads(s)
        
    return _parse_scalar(typ, s)

def _serialize(obj, typ):
    # 将对象转回 Python list/dict 以便对比和打印
    if typ == "ListNode":
        return _link_to_list(obj)
    if typ == "TreeNode":
        return _tree_to_list(obj)
    return obj

def run():
    if __META__ is None: return
    if __META__.get("className"):
        print("设计类暂不支持。")
        return

    fn_name = __META__.get("name")
    params = __META__.get("params") or []
    ret_ts = __META__.get("return") or __META__.get("ret")

    p = Path("testcases.txt")
    if not p.exists(): return
    
    text = p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    
    sol = Solution()
    fn = getattr(sol, fn_name)

    for idx, block in enumerate(blocks, 1):
        lines = [ln.strip() for ln in block.splitlines()]
        in_lines = []
        out_line = ""
        mode = ""
        for ln in lines:
            if ln == "input:": mode = "in"
            elif ln == "output:": mode = "out"
            elif mode == "in": in_lines.append(ln)
            elif mode == "out" and ln: out_line = ln
            
        if len(in_lines) < len(params): continue

        try:
            # 解析输入参数
            args = []
            for i, spec in enumerate(params):
                val = _parse_value(spec, in_lines[i])
                args.append(val)

            # 执行
            got_obj = fn(*args)
            
            # 序列化结果以便对比
            got_raw = _serialize(got_obj, ret_ts.get("type"))
            
            # 解析期望输出 (用于对比)
            expected_raw = None
            if out_line:
                # 期望输出通常是 JSON 格式的 [7, 0, 8]
                # 注意：这里我们不需要构建 ListNode 对象，直接对比 list 数据即可
                # 所以直接 json.loads
                try:
                    expected_raw = json.loads(out_line)
                except:
                    expected_raw = out_line # fallback

            print(f"Test {idx}:")
            print(f"  Input: {in_lines[:len(params)]}")
            print(f"  Got:   {got_raw}")
            if expected_raw is not None:
                print(f"  Exp:   {expected_raw}")
                if got_raw == expected_raw:
                    print("  ✅ Passed")
                else:
                    print("  ❌ Failed")
            else:
                print("  (No output spec)")
            print("-" * 20)

        except Exception as e:
            print(f"Test {idx} Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run()
