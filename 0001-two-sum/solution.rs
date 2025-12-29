
pub struct Solution;

impl Solution {
    pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
        
    }
}

// --- Test Runner ---
fn parse_int_vec(s: &str) -> Vec<i32> {
    let s = s.trim();
    if s == "[]" { return vec![]; }
    let s = s.trim_start_matches('[').trim_end_matches(']');
    s.split(',').map(|x| x.trim().parse().unwrap()).collect()
}

fn main() {
    use std::fs;
    let content = fs::read_to_string("testcases.txt").expect("testcases.txt not found");
    let blocks: Vec<&str> = content.split("\n\n").filter(|b| !b.trim().is_empty()).collect();
    
    for (i, block) in blocks.iter().enumerate() {
        println!("Test {}:", i + 1);
        
        let raw_lines: Vec<&str> = block.lines().collect();
        let mut lines = Vec::new();
        let mut expected = None;
        let mut is_input = false;
        
        for line in raw_lines {
            if line.starts_with("input:") {
                is_input = true;
            } else if line.starts_with("output:") {
                is_input = false;
                let inline = line.strip_prefix("output:").unwrap().trim();
                if !inline.is_empty() {
                    expected = Some(inline.to_string());
                }
            } else if is_input {
                lines.push(line);
            } else if !is_input && expected.is_none() && !line.trim().is_empty() {
                expected = Some(line.trim().to_string());
            }
        }
        
        if lines.len() < 2 { continue; }
        
        let arg0 = parse_int_vec(lines[0]);
        let arg1 = lines[1].trim().parse::<i32>().unwrap();
        
        let result = Solution::two_sum(arg0, arg1);
        // 打印输入
        println!("  Input: {:?}", &lines[0..2.min(lines.len())]);
        
        println!("  Got: {}", format!("{:?}", result));
        
        if let Some(exp_str) = expected {
            let exp = parse_int_vec(&exp_str);
            println!("  Exp: {:?}", exp);
            if result == exp {
                println!("  ✅ Passed");
            } else {
                println!("  ❌ Failed");
            }
        } else {
            println!("  (No expected output)");
        }
        println!("--------------------");
    }
}
