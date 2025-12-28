#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <cmath>
#include <regex>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        int n = nums.size();
        for (int i = 0; i < n; ++i) {
          for (int j = i + 1; j < n; ++j) {
            if (nums[i] + nums[j] == target) {
              return {i, j};
            }
          }
        }
        return {};
    }
};


static inline string trim(const string& s) {
    size_t i = 0, j = s.size();
    while (i < j && isspace((unsigned char)s[i])) i++;
    while (j > i && isspace((unsigned char)s[j-1])) j--;
    return s.substr(i, j - i);
}

static inline string trimBrackets(string s) {
    s = trim(s);
    if (s.size() >= 2 && s.front() == '[' && s.back() == ']') {
        return trim(s.substr(1, s.size()-2));
    }
    return s;
}

static vector<string> splitTopLevel(const string& inner) {
    vector<string> items;
    string buf;
    int depth = 0;
    bool inStr = false, esc = false;
    for (char ch : inner) {
        if (inStr) {
            buf.push_back(ch);
            if (esc) esc = false;
            else if (ch == '\\') esc = true;
            else if (ch == '"') inStr = false;
            continue;
        }
        if (ch == '"') { inStr = true; buf.push_back(ch); continue; }
        if (ch == '[') { depth++; buf.push_back(ch); continue; }
        if (ch == ']') { depth--; buf.push_back(ch); continue; }
        if (ch == ',' && depth == 0) {
            items.push_back(trim(buf));
            buf.clear();
            continue;
        }
        buf.push_back(ch);
    }
    if (!trim(buf).empty()) items.push_back(trim(buf));
    return items;
}

static string parseString(string s) {
    s = trim(s);
    if (s.size() >= 2) {
        char a = s.front(), b = s.back();
        if ((a=='"' && b=='"') || (a=='\'' && b=='\'')) {
            return s.substr(1, s.size()-2);
        }
    }
    return s;
}
static bool parseBool(string s) {
    s = trim(s);
    for (auto& c: s) c = (char)tolower(c);
    return s == "true" || s == "1";
}
static int parseInt(string s) { return stoi(trim(s)); }
static long long parseLong(string s) { return stoll(trim(s)); }
static double parseDouble(string s) { return stod(trim(s)); }

static vector<int> parseIntVec(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<int> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseInt(p));
    return out;
}
static vector<vector<int>> parseInt2D(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<vector<int>> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseIntVec(p));
    return out;
}

static vector<long long> parseLongVec(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<long long> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseLong(p));
    return out;
}
static vector<vector<long long>> parseLong2D(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<vector<long long>> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseLongVec(p));
    return out;
}

static vector<double> parseDoubleVec(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<double> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseDouble(p));
    return out;
}
static vector<vector<double>> parseDouble2D(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<vector<double>> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseDoubleVec(p));
    return out;
}

static vector<bool> parseBoolVec(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<bool> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseBool(p));
    return out;
}
static vector<vector<bool>> parseBool2D(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<vector<bool>> out;
    out.reserve(parts.size());
    for (auto &p : parts) {
        auto v = parseBoolVec(p);
        out.emplace_back(v.begin(), v.end());
    }
    return out;
}

static vector<string> parseStringVec(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<string> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseString(p));
    return out;
}
static vector<vector<string>> parseString2D(string s) {
    string inner = trimBrackets(s);
    if (inner.empty()) return {};
    auto parts = splitTopLevel(inner);
    vector<vector<string>> out;
    out.reserve(parts.size());
    for (auto &p : parts) out.push_back(parseStringVec(p));
    return out;
}

static bool equalDoubleVec(const vector<double>& a, const vector<double>& b) {
    if (a.size() != b.size()) return false;
    for (size_t i=0;i<a.size();i++) if (fabs(a[i]-b[i]) > 1e-6) return false;
    return true;
}
static bool equalDouble2D(const vector<vector<double>>& a, const vector<vector<double>>& b) {
    if (a.size() != b.size()) return false;
    for (size_t i=0;i<a.size();i++) if (!equalDoubleVec(a[i], b[i])) return false;
    return true;
}

static vector<string> splitCases(const string& content) {
    string s = content;
    // normalize newlines
    s.erase(std::remove(s.begin(), s.end(), '\r'), s.end());

    vector<string> cases;
    size_t start = 0;
    while (true) {
        size_t pos = s.find("\n\n", start);
        string blk = (pos == string::npos) ? s.substr(start) : s.substr(start, pos-start);
        blk = trim(blk);
        if (!blk.empty()) cases.push_back(blk);
        if (pos == string::npos) break;
        start = pos + 2;
    }
    return cases;
}

static pair<vector<string>, string> readCase(const string& block) {
    vector<string> inLines;
    string outStr;
    string mode;
    stringstream ss(block);
    string line;
    while (getline(ss, line)) {
        string t = trim(line);
        if (t == "input:") { mode = "in"; continue; }
        if (t == "output:") { mode = "out"; continue; }
        if (mode == "in") inLines.push_back(t);
        else if (mode == "out") if (!t.empty()) outStr += t;
    }
    return {inLines, trim(outStr)};
}

int main() {
    ifstream f("testcases.txt");
    if (!f.is_open()) {
        cout << "testcases.txt not found\n";
        return 0;
    }
    string content((istreambuf_iterator<char>(f)), istreambuf_iterator<char>());
    auto cases = splitCases(content);

    for (int ci=0; ci<(int)cases.size(); ci++) {
        auto [inLines, outStr] = readCase(cases[ci]);
        if ((int)inLines.size() < 2) {
            cout << "Test " << (ci+1) << ": 输入行数不足，期望 2 行，实际 " << inLines.size() << " 行\n";
            continue;
        }

        std::vector<int> arg0 = parseIntVec(inLines[0]);
        int arg1 = parseInt(inLines[1]);
        auto got = Solution().twoSum(arg0, arg1);
        std::vector<int> expected = parseIntVec(outStr);
        bool passed = (got == expected);

        cout << "Test " << (ci+1) << ": " << (passed ? "Passed" : "Failed") << "\n";
        cout << " Input(raw): ";
        for (int k = 0; k < inLines.size(); k++) cout << inLines[k] << (k+1==inLines.size()? "" : " | ");
        cout << "\n";
        cout << " Expected(raw): " << outStr << "\n";
        cout << " Done\n\n";
    }
    return 0;
}
