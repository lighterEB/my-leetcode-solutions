package main

import (
    "encoding/json"
    "fmt"
    "os"
    "strings"
)


func twoSum(nums []int, target int) []int {
    
}

// --- Test Runner ---
func main() {
    data, err := os.ReadFile("testcases.txt")
    if err != nil {
        fmt.Println("testcases.txt not found")
        return
    }
    
    content := string(data)
    content = strings.ReplaceAll(content, "\r\n", "\n")
    blocks := strings.Split(content, "\n\n")
    
    testNum := 0
    for _, block := range blocks {
        block = strings.TrimSpace(block)
        if block == "" {
            continue
        }
        testNum++
        
        rawLines := strings.Split(block, "\n")
        var lines []string
        var expected string
        isInput := false
        
        for _, line := range rawLines {
            if strings.HasPrefix(line, "input:") {
                isInput = true
            } else if strings.HasPrefix(line, "output:") {
                isInput = false
                inline := strings.TrimSpace(strings.TrimPrefix(line, "output:"))
                if inline != "" {
                    expected = inline
                }
            } else if isInput {
                lines = append(lines, strings.TrimSpace(line))
            } else if !isInput && expected == "" && strings.TrimSpace(line) != "" {
                expected = strings.TrimSpace(line)
            }
        }
        
        if len(lines) < 2 {
            continue
        }
        
        fmt.Printf("Test %d:\n", testNum)
        
        var arg0 []int
        json.Unmarshal([]byte(lines[0]), &arg0)
        var arg1 int
        json.Unmarshal([]byte(lines[1]), &arg1)
        
        result := twoSum(arg0, arg1)
        // 打印输入
        inputSlice := lines
        if len(lines) > 2 {
            inputSlice = lines[:2]
        }
        fmt.Printf("  Input: %v\n", inputSlice)
        
        fmt.Printf("  Got: %v\n", result)
        
        if expected != "" {
            var exp []int
            json.Unmarshal([]byte(expected), &exp)
            fmt.Printf("  Exp: %v\n", exp)
            
            if fmt.Sprint(result) == fmt.Sprint(exp) {
                fmt.Println("  ✅ Passed")
            } else {
                fmt.Println("  ❌ Failed")
            }
        } else {
            fmt.Println("  (No expected output)")
        }
        fmt.Println("--------------------")
    }
}
