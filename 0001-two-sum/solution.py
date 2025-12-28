class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        map = dict()
        for i in range(len(nums)):
            if target - nums[i] in map:
                return [map.get(target - nums[i]), i]
            map[nums[i]] = i


import math
from pathlib import Path
import json
def _split_cases(text: str):
    blocks = [b.strip("\n") for b in text.replace("\r\n","\n").replace("\r","\n").split("\n\n") if b.strip()]
    return blocks

def _parse_scalar(base: str, s: str):
    s = s.strip()
    if base == "string":
        # 尝试 JSON 字符串（含引号），否则原样
        if (len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"))):
            try:
                return json.loads(s.replace("'", '"')) if s[0] == "'" else json.loads(s)
            except Exception:
                return s[1:-1]
        return s
    if base == "boolean":
        if s.lower() in ("true", "1"): return True
        if s.lower() in ("false", "0"): return False
        raise ValueError("bad boolean: " + s)
    if base == "double":
        return float(s)
    if base == "long":
        return int(s)
    # integer
    return int(s)

def _split_top_level(inner: str):
    items = []
    buf = []
    depth = 0
    in_str = False
    esc = False
    for ch in inner:
        if in_str:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == "\\":  # escape
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            buf.append(ch)
            continue
        if ch == '[':
            depth += 1
            buf.append(ch)
            continue
        if ch == ']':
            depth -= 1
            buf.append(ch)
            continue
        if ch == ',' and depth == 0:
            items.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        items.append(tail)
    return items

def _parse_array(base: str, dims: int, s: str):
    s = s.strip()
    if s == "[]": return []
    if not (s.startswith('[') and s.endswith(']')):
        raise ValueError("bad array: " + s)
    inner = s[1:-1].strip()
    if inner == "":
        return []
    parts = _split_top_level(inner)
    if dims == 1:
        return [_parse_scalar(base, x) for x in parts]
    if dims == 2:
        return [_parse_array(base, 1, x) for x in parts]
    raise ValueError("dims>2 not supported")
def lc_type_dims(t: str):
    # "integer[][]" -> ("integer", 2)
    base = t
    dims = 0
    while base.endswith("[]"):
        dims += 1
        base = base[:-2]
    return base, dims
def _parse_by_type(t: str, s: str):
    base, dims = lc_type_dims(t)
    return _parse_scalar(base, s) if dims == 0 else _parse_array(base, dims, s)

def _equal_by_type(t: str, a, b) -> bool:
    base, dims = lc_type_dims(t)
    if base == "double":
        if dims == 0:
            return abs(a - b) <= 1e-6
        # array of doubles
        return json.dumps(a) == json.dumps(b) if dims == 2 else all(abs(x-y)<=1e-6 for x,y in zip(a,b))
    return a == b

def _read_case(block: str):
    lines = [ln.strip() for ln in block.splitlines()]
    in_mode = None
    ins = []
    outs = []
    for ln in lines:
        if ln == "input:":
            in_mode = "in"
            continue
        if ln == "output:":
            in_mode = "out"
            continue
        if in_mode == "in":
            ins.append(ln)
        elif in_mode == "out":
            outs.append(ln)
    return ins, "\n".join(outs).strip()

def _run_tests():
    p = Path("testcases.txt")
    if not p.exists():
        print("testcases.txt 不存在")
        return
    content = p.read_text(encoding="utf-8")
    cases = _split_cases(content)
    meta_name = 'twoSum'
    param_types = ['integer[]', 'integer']
    ret_type = 'integer[]'

    for idx, block in enumerate(cases, 1):
        in_lines, out_str = _read_case(block)
        if len(in_lines) < 2:
            print(f"Test {idx}: 输入行数不足，期望 2 行，实际 {len(in_lines)} 行")
            continue

        args = []
        for i, t in enumerate(param_types):
            args.append(_parse_by_type(t, in_lines[i]))

        sol = Solution()
        fn = getattr(sol, meta_name)
        got = fn(*args)

        if ret_type and out_str:
            expected = _parse_by_type(ret_type, out_str.splitlines()[0] if lc_type_dims(ret_type)[1]==0 else out_str.splitlines()[0])
            # 对数组允许 output 多行时，仍然把整段拼回去
            if lc_type_dims(ret_type)[1] > 0:
                expected = _parse_by_type(ret_type, out_str.replace("\n",""))
            passed = _equal_by_type(ret_type, got, expected)
            print(f"Test {idx}: {'Passed' if passed else 'Failed'}")
            print(" Input:", args)
            print(" Expected:", expected)
            print(" Got:", got, "\n")
        else:
            print(f"Test {idx}: Done (no expected output)")
            print(" Input:", args)
            print(" Got:", got, "\n")

if __name__ == "__main__":
    _run_tests()
