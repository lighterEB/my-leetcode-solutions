pub struct Solution;

impl Solution {
    pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
        
    }
}


use std::fs;
use std::path::Path;

fn trim(s: &str) -> String {
    s.trim().to_string()
}

fn trim_brackets(s: &str) -> String {
    let t = s.trim();
    if t.starts_with('[') && t.ends_with(']') && t.len() >= 2 {
        t[1..t.len()-1].trim().to_string()
    } else {
        t.to_string()
    }
}

fn split_top_level(inner: &str) -> Vec<String> {
    let mut items: Vec<String> = vec![];
    let mut buf = String::new();
    let mut depth: i32 = 0;
    let mut in_str = false;
    let mut esc = false;

    for ch in inner.chars() {
        if in_str {
            buf.push(ch);
            if esc {
                esc = false;
            } else if ch == '\\' {
                esc = true;
            } else if ch == '"' {
                in_str = false;
            }
            continue;
        }
        if ch == '"' {
            in_str = true;
            buf.push(ch);
            continue;
        }
        if ch == '[' {
            depth += 1;
            buf.push(ch);
            continue;
        }
        if ch == ']' {
            depth -= 1;
            buf.push(ch);
            continue;
        }
        if ch == ',' && depth == 0 {
            let t = buf.trim().to_string();
            if !t.is_empty() { items.push(t); }
            buf.clear();
            continue;
        }
        buf.push(ch);
    }
    let tail = buf.trim().to_string();
    if !tail.is_empty() { items.push(tail); }
    items
}

fn parse_string(s: &str) -> String {
    let t = s.trim();
    if t.len() >= 2 {
        let a = t.chars().next().unwrap();
        let b = t.chars().last().unwrap();
        if (a == '"' && b == '"') || (a == '\'' && b == '\'') {
            return t[1..t.len()-1].to_string();
        }
    }
    t.to_string()
}
fn parse_bool(s: &str) -> bool {
    let t = s.trim().to_lowercase();
    t == "true" || t == "1"
}
fn parse_i32(s: &str) -> i32 { s.trim().parse::<i32>().unwrap() }
fn parse_i64(s: &str) -> i64 { s.trim().parse::<i64>().unwrap() }
fn parse_f64(s: &str) -> f64 { s.trim().parse::<f64>().unwrap() }

fn parse_vec_i32(s: &str) -> Vec<i32> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_i32(x)).collect()
}
fn parse_2d_i32(s: &str) -> Vec<Vec<i32>> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_vec_i32(x)).collect()
}

fn parse_vec_i64(s: &str) -> Vec<i64> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_i64(x)).collect()
}
fn parse_2d_i64(s: &str) -> Vec<Vec<i64>> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_vec_i64(x)).collect()
}

fn parse_vec_f64(s: &str) -> Vec<f64> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_f64(x)).collect()
}
fn parse_2d_f64(s: &str) -> Vec<Vec<f64>> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_vec_f64(x)).collect()
}

fn parse_vec_bool(s: &str) -> Vec<bool> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_bool(x)).collect()
}
fn parse_2d_bool(s: &str) -> Vec<Vec<bool>> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_vec_bool(x)).collect()
}

fn parse_vec_string(s: &str) -> Vec<String> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_string(x)).collect()
}
fn parse_2d_string(s: &str) -> Vec<Vec<String>> {
    let inner = trim_brackets(s);
    if inner.trim().is_empty() { return vec![]; }
    split_top_level(&inner).iter().map(|x| parse_vec_string(x)).collect()
}

fn equal_f64_vec(a: &Vec<f64>, b: &Vec<f64>) -> bool {
    if a.len() != b.len() { return false; }
    for i in 0..a.len() {
        if (a[i] - b[i]).abs() > 1e-6 { return false; }
    }
    true
}
fn equal_f64_2d(a: &Vec<Vec<f64>>, b: &Vec<Vec<f64>>) -> bool {
    if a.len() != b.len() { return false; }
    for i in 0..a.len() {
        if !equal_f64_vec(&a[i], &b[i]) { return false; }
    }
    true
}

fn split_cases(content: &str) -> Vec<String> {
    let s = content.replace("\r\n", "\n").replace("\r", "\n");
    s.split("\n\n")
        .map(|b| b.trim().to_string())
        .filter(|b| !b.is_empty())
        .collect()
}

fn read_case(block: &str) -> (Vec<String>, String) {
    let mut mode = "";
    let mut ins: Vec<String> = vec![];
    let mut out = String::new();
    for line in block.lines() {
        let t = line.trim();
        if t == "input:" { mode = "in"; continue; }
        if t == "output:" { mode = "out"; continue; }
        if mode == "in" { ins.push(t.to_string()); }
        else if mode == "out" { if !t.is_empty() { out.push_str(t); } }
    }
    (ins, out.trim().to_string())
}

fn main() {
    let p = Path::new("testcases.txt");
    if !p.exists() {
        println!("testcases.txt not found");
        return;
    }
    let content = fs::read_to_string(p).unwrap();
    let cases = split_cases(&content);

    for (i, block) in cases.iter().enumerate() {
        let (in_lines, out_str) = read_case(block);
        if in_lines.len() < 2 {
            println!("Test {}: 输入行数不足，期望 2 行，实际 {} 行", i+1, in_lines.len());
            continue;
        }

        let arg0: Vec<i32> = parse_vec_i32(in_lines[0].as_str());
        let arg1: i32 = parse_i32(in_lines[1].as_str());
        let got = Solution::two_sum(arg0, arg1);
        let expected: Vec<i32> = parse_vec_i32(out_str.as_str());
        let passed = got == expected;

        println!("Test {}: {}", i+1, if passed {"Passed"} else {"Failed"});
        println!(" Input(raw): {:?}", &in_lines[0..2]);
        println!(" Expected(raw): {}", out_str);
        println!();
    }
}
