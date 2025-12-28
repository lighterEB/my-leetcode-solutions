package main

import (
    "bufio"
    "fmt"
    "os"
    "sort"
    "strconv"
    "strings"
)
        

func twoSum(nums []int, target int) []int {
	for index, value := range nums {
		for i, v := range nums[index + 1:] {
			if value + v == target {
				return []int{index, i + index + 1}
			}
		}
	}
	return []int{}
}


func splitCases(content string) []string {
    content = strings.ReplaceAll(content, "\r\n", "\n")
    content = strings.ReplaceAll(content, "\r", "\n")
    parts := strings.Split(content, "\n\n")
    out := make([]string, 0)
    for _, p := range parts {
        p = strings.TrimSpace(p)
        if p != "" {
            out = append(out, p)
        }
    }
    return out
}

func readCase(block string) ([]string, string) {
    lines := strings.Split(block, "\n")
    mode := ""
    inLines := make([]string, 0)
    outLines := make([]string, 0)
    for _, ln := range lines {
        t := strings.TrimSpace(ln)
        if t == "input:" {
            mode = "in"
            continue
        }
        if t == "output:" {
            mode = "out"
            continue
        }
        if mode == "in" {
            inLines = append(inLines, t)
        } else if mode == "out" {
            if t != "" {
                outLines = append(outLines, t)
            }
        }
    }
    return inLines, strings.TrimSpace(strings.Join(outLines, ""))
}

func trimBrackets(s string) string {
    s = strings.TrimSpace(s)
    if strings.HasPrefix(s, "[") && strings.HasSuffix(s, "]") {
        return strings.TrimSpace(s[1:len(s)-1])
    }
    return s
}

func splitTopLevel(inner string) []string {
    items := make([]string, 0)
    buf := make([]rune, 0)
    depth := 0
    inStr := false
    esc := false
    for _, ch := range inner {
        if inStr {
            buf = append(buf, ch)
            if esc {
                esc = false
            } else if ch == '\\' {
                esc = true
            } else if ch == '"' {
                inStr = false
            }
            continue
        }
        if ch == '"' {
            inStr = true
            buf = append(buf, ch)
            continue
        }
        if ch == '[' {
            depth++
            buf = append(buf, ch)
            continue
        }
        if ch == ']' {
            depth--
            buf = append(buf, ch)
            continue
        }
        if ch == ',' && depth == 0 {
            items = append(items, strings.TrimSpace(string(buf)))
            buf = make([]rune, 0)
            continue
        }
        buf = append(buf, ch)
    }
    tail := strings.TrimSpace(string(buf))
    if tail != "" {
        items = append(items, tail)
    }
    return items
}

func parseString(s string) string {
    s = strings.TrimSpace(s)
    if len(s) >= 2 && ((s[0] == '"' && s[len(s)-1] == '"') || (s[0] == '\'' && s[len(s)-1] == '\'')) {
        return s[1:len(s)-1]
    }
    return s
}
func parseBool(s string) bool {
    s = strings.ToLower(strings.TrimSpace(s))
    return s == "true" || s == "1"
}
func parseInt(s string) int {
    v, _ := strconv.Atoi(strings.TrimSpace(s))
    return v
}
func parseInt64(s string) int64 {
    v, _ := strconv.ParseInt(strings.TrimSpace(s), 10, 64)
    return v
}
func parseFloat64(s string) float64 {
    v, _ := strconv.ParseFloat(strings.TrimSpace(s), 64)
    return v
}

func parseIntSlice(s string) []int {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return []int{}
    }
    parts := splitTopLevel(inner)
    out := make([]int, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseInt(p))
    }
    return out
}
func parseInt2D(s string) [][]int {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return [][]int{}
    }
    parts := splitTopLevel(inner)
    out := make([][]int, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseIntSlice(p))
    }
    return out
}

func parseInt64Slice(s string) []int64 {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return []int64{}
    }
    parts := splitTopLevel(inner)
    out := make([]int64, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseInt64(p))
    }
    return out
}
func parseInt642D(s string) [][]int64 {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return [][]int64{}
    }
    parts := splitTopLevel(inner)
    out := make([][]int64, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseInt64Slice(p))
    }
    return out
}

func parseFloat64Slice(s string) []float64 {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return []float64{}
    }
    parts := splitTopLevel(inner)
    out := make([]float64, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseFloat64(p))
    }
    return out
}
func parseFloat642D(s string) [][]float64 {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return [][]float64{}
    }
    parts := splitTopLevel(inner)
    out := make([][]float64, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseFloat64Slice(p))
    }
    return out
}

func parseBoolSlice(s string) []bool {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return []bool{}
    }
    parts := splitTopLevel(inner)
    out := make([]bool, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseBool(p))
    }
    return out
}
func parseBool2D(s string) [][]bool {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return [][]bool{}
    }
    parts := splitTopLevel(inner)
    out := make([][]bool, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseBoolSlice(p))
    }
    return out
}

func parseStringSlice(s string) []string {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return []string{}
    }
    parts := splitTopLevel(inner)
    out := make([]string, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseString(p))
    }
    return out
}
func parseString2D(s string) [][]string {
    inner := trimBrackets(s)
    if strings.TrimSpace(inner) == "" {
        return [][]string{}
    }
    parts := splitTopLevel(inner)
    out := make([][]string, 0, len(parts))
    for _, p := range parts {
        out = append(out, parseStringSlice(p))
    }
    return out
}

func equal(a any, b any) bool {
    // 针对 []int 返回题常见：允许无序比较（如 two-sum）
    // 这里做一个保守策略：如果是 []int / []int64 则排序后比较；其它类型按 fmt.Sprint 比较
    switch x := a.(type) {
    case []int:
        y, ok := b.([]int); if !ok { return false }
        xx := append([]int{}, x...)
        yy := append([]int{}, y...)
        sort.Ints(xx); sort.Ints(yy)
        if len(xx) != len(yy) { return false }
        for i := range xx { if xx[i] != yy[i] { return false } }
        return true
    default:
        return fmt.Sprint(a) == fmt.Sprint(b)
    }
}

func main() {
    // 读取 testcases.txt
    f, err := os.Open("testcases.txt")
    if err != nil {
        fmt.Println("testcases.txt not found")
        return
    }
    defer f.Close()

    buf := new(strings.Builder)
    sc := bufio.NewScanner(f)
    for sc.Scan() {
        buf.WriteString(sc.Text())
        buf.WriteString("\n")
    }
    cases := splitCases(buf.String())

    for i, c := range cases {
        inLines, outStr := readCase(c)
        if len(inLines) < 2 {
            fmt.Printf("Test %d: 输入行数不足，期望 2 行，实际 %d 行\n", i+1, len(inLines))
            continue
        }
    arg0 := parseIntSlice(inLines[0])
    arg1 := parseInt(inLines[1])
        got := twoSum(arg0, arg1)
    expected := parseIntSlice(outStr)
    passed := equal(got, expected)
        fmt.Printf("Test %d: %s\n", i+1, map[bool]string{true:"Passed", false:"Failed"}[passed])
        fmt.Printf(" Input: %v\n", inLines[:2])
        fmt.Printf(" Expected: %v\n", outStr)
        fmt.Printf(" Got: %v\n\n", got)
    }
}
