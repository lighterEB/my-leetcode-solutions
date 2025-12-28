import java.util.Map;
import java.util.HashMap;

class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; ++i) {
          if (map.containsKey(target - nums[i])) {
            int[] line = new int[]{map.get(target - nums[i]), i};
            return line;
          }
          map.put(nums[i], i);
        }
        return new int[]{};
    }
}


class Main {

    static java.util.List<String> splitCases(String content) {
        content = content.replace("\r\n", "\n").replace("\r", "\n");
        String[] parts = content.split("\n\n");
        java.util.List<String> out = new java.util.ArrayList<>();
        for (String p : parts) {
            p = p.trim();
            if (!p.isEmpty()) out.add(p);
        }
        return out;
    }

    static class CaseData {
        java.util.List<String> inLines;
        String outStr;
        CaseData(java.util.List<String> inLines, String outStr) {
            this.inLines = inLines;
            this.outStr = outStr;
        }
    }

    static CaseData readCase(String block) {
        String[] lines = block.split("\n");
        String mode = "";
        java.util.List<String> ins = new java.util.ArrayList<>();
        StringBuilder outs = new StringBuilder();
        for (String ln : lines) {
            String t = ln.trim();
            if (t.equals("input:")) { mode = "in"; continue; }
            if (t.equals("output:")) { mode = "out"; continue; }
            if (mode.equals("in")) {
                ins.add(t);
            } else if (mode.equals("out")) {
                if (!t.isEmpty()) outs.append(t);
            }
        }
        return new CaseData(ins, outs.toString().trim());
    }

    static String trimBrackets(String s) {
        s = s.trim();
        if (s.startsWith("[") && s.endsWith("]") && s.length() >= 2) {
            return s.substring(1, s.length() - 1).trim();
        }
        return s;
    }

    static java.util.List<String> splitTopLevel(String inner) {
        java.util.List<String> items = new java.util.ArrayList<>();
        StringBuilder buf = new StringBuilder();
        int depth = 0;
        boolean inStr = false;
        boolean esc = false;

        for (int i = 0; i < inner.length(); i++) {
            char ch = inner.charAt(i);

            if (inStr) {
                buf.append(ch);
                if (esc) esc = false;
                else if (ch == '\\') esc = true;
                else if (ch == '"') inStr = false;
                continue;
            }

            if (ch == '"') {
                inStr = true;
                buf.append(ch);
                continue;
            }
            if (ch == '[') { depth++; buf.append(ch); continue; }
            if (ch == ']') { depth--; buf.append(ch); continue; }

            if (ch == ',' && depth == 0) {
                String t = buf.toString().trim();
                if (!t.isEmpty()) items.add(t);
                buf.setLength(0);
                continue;
            }
            buf.append(ch);
        }
        String tail = buf.toString().trim();
        if (!tail.isEmpty()) items.add(tail);
        return items;
    }

    static String parseString(String s) {
        s = s.trim();
        if (s.length() >= 2) {
            char a = s.charAt(0), b = s.charAt(s.length()-1);
            if ((a=='"' && b=='"') || (a=='\'' && b=='\'')) {
                return s.substring(1, s.length()-1);
            }
        }
        return s;
    }

    static boolean parseBool(String s) {
        s = s.trim().toLowerCase();
        return s.equals("true") || s.equals("1");
    }

    static int parseInt(String s) { return Integer.parseInt(s.trim()); }
    static long parseLong(String s) { return Long.parseLong(s.trim()); }
    static double parseDouble(String s) { return Double.parseDouble(s.trim()); }

    static int[] parseIntArray(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new int[0];
        java.util.List<String> parts = splitTopLevel(inner);
        int[] out = new int[parts.size()];
        for (int i=0;i<parts.size();i++) out[i] = parseInt(parts.get(i));
        return out;
    }

    static int[][] parseInt2D(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new int[0][];
        java.util.List<String> parts = splitTopLevel(inner);
        int[][] out = new int[parts.size()][];
        for (int i=0;i<parts.size();i++) out[i] = parseIntArray(parts.get(i));
        return out;
    }

    static long[] parseLongArray(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new long[0];
        java.util.List<String> parts = splitTopLevel(inner);
        long[] out = new long[parts.size()];
        for (int i=0;i<parts.size();i++) out[i] = parseLong(parts.get(i));
        return out;
    }

    static long[][] parseLong2D(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new long[0][];
        java.util.List<String> parts = splitTopLevel(inner);
        long[][] out = new long[parts.size()][];
        for (int i=0;i<parts.size();i++) out[i] = parseLongArray(parts.get(i));
        return out;
    }

    static double[] parseDoubleArray(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new double[0];
        java.util.List<String> parts = splitTopLevel(inner);
        double[] out = new double[parts.size()];
        for (int i=0;i<parts.size();i++) out[i] = parseDouble(parts.get(i));
        return out;
    }

    static double[][] parseDouble2D(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new double[0][];
        java.util.List<String> parts = splitTopLevel(inner);
        double[][] out = new double[parts.size()][];
        for (int i=0;i<parts.size();i++) out[i] = parseDoubleArray(parts.get(i));
        return out;
    }

    static boolean[] parseBoolArray(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new boolean[0];
        java.util.List<String> parts = splitTopLevel(inner);
        boolean[] out = new boolean[parts.size()];
        for (int i=0;i<parts.size();i++) out[i] = parseBool(parts.get(i));
        return out;
    }

    static boolean[][] parseBool2D(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new boolean[0][];
        java.util.List<String> parts = splitTopLevel(inner);
        boolean[][] out = new boolean[parts.size()][];
        for (int i=0;i<parts.size();i++) out[i] = parseBoolArray(parts.get(i));
        return out;
    }

    static String[] parseStringArray(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new String[0];
        java.util.List<String> parts = splitTopLevel(inner);
        String[] out = new String[parts.size()];
        for (int i=0;i<parts.size();i++) out[i] = parseString(parts.get(i));
        return out;
    }

    static String[][] parseString2D(String s) {
        String inner = trimBrackets(s);
        if (inner.isEmpty()) return new String[0][];
        java.util.List<String> parts = splitTopLevel(inner);
        String[][] out = new String[parts.size()][];
        for (int i=0;i<parts.size();i++) out[i] = parseStringArray(parts.get(i));
        return out;
    }

    static boolean equalDoubleArray(double[] a, double[] b) {
        if (a == null || b == null) return a == b;
        if (a.length != b.length) return false;
        for (int i=0;i<a.length;i++) if (Math.abs(a[i]-b[i]) > 1e-6) return false;
        return true;
    }

    static boolean equalDouble2D(double[][] a, double[][] b) {
        if (a == null || b == null) return a == b;
        if (a.length != b.length) return false;
        for (int i=0;i<a.length;i++) if (!equalDoubleArray(a[i], b[i])) return false;
        return true;
    }

    public static void main(String[] args) throws Exception {
        java.nio.file.Path p = java.nio.file.Paths.get("testcases.txt");
        if (!java.nio.file.Files.exists(p)) {
            System.out.println("testcases.txt not found");
            return;
        }
        byte[] bytes = java.nio.file.Files.readAllBytes(p);
        String content = new String(bytes, java.nio.charset.StandardCharsets.UTF_8);

        java.util.List<String> cases = splitCases(content);

        for (int ci=0; ci<cases.size(); ci++) {
            CaseData c = readCase(cases.get(ci));
            java.util.List<String> inLines = c.inLines;
            String outStr = c.outStr;

            if (inLines.size() < 2) {
                System.out.printf("Test %d: 输入行数不足，期望 2 行，实际 %d 行\n", ci+1, inLines.size());
                continue;
            }

            int[] arg0 = parseIntArray(inLines.get(0));
            int arg1 = parseInt(inLines.get(1));
            var got = new Solution().twoSum(arg0, arg1);

            if (!outStr.isEmpty()) {
            int[] expected = parseIntArray(outStr);
            boolean passed = java.util.Arrays.equals(got, expected);
                System.out.println("Test " + (ci+1) + ": " + (passed ? "Passed" : "Failed"));
                System.out.println(" Input(raw): " + inLines.subList(0, 2));
                System.out.println(" Expected(raw): " + outStr);
                System.out.println();
            } else {
                System.out.println("Test " + (ci+1) + ": Done (no expected output)");
                System.out.println();
            }
        }
    }
}
