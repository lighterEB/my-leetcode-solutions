# 1. Two Sum

**难度**：Easy

**链接**：https://leetcode.cn/problems/two-sum/

## 题目描述

<p>Given an array of integers <code>nums</code>&nbsp;and an integer <code>target</code>, return <em>indices of the two numbers such that they add up to <code>target</code></em>.</p>

<p>You may assume that each input would have <strong><em>exactly</em> one solution</strong>, and you may not use the <em>same</em> element twice.</p>

<p>You can return the answer in any order.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> nums = [2,7,11,15], target = 9
<strong>Output:</strong> [0,1]
<strong>Explanation:</strong> Because nums[0] + nums[1] == 9, we return [0, 1].
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> nums = [3,2,4], target = 6
<strong>Output:</strong> [1,2]
</pre>

<p><strong class="example">Example 3:</strong></p>

<pre>
<strong>Input:</strong> nums = [3,3], target = 6
<strong>Output:</strong> [0,1]
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>2 &lt;= nums.length &lt;= 10<sup>4</sup></code></li>
	<li><code>-10<sup>9</sup> &lt;= nums[i] &lt;= 10<sup>9</sup></code></li>
	<li><code>-10<sup>9</sup> &lt;= target &lt;= 10<sup>9</sup></code></li>
	<li><strong>Only one valid answer exists.</strong></li>
</ul>

<p>&nbsp;</p>
<strong>Follow-up:&nbsp;</strong>Can you come up with an algorithm that is less than <code>O(n<sup>2</sup>)</code><font face="monospace">&nbsp;</font>time complexity?

## 本地测试说明

- `testcases.txt`：每组用例由 `input:` + 若干行参数 + `output:` + 预期输出组成，用空行分隔。
- 已尝试从题面示例自动填充 output；未识别到的 output 会留空，需要你手动补齐。
- runner 会根据题目 `metaData` 动态生成（若题型超出当前支持范围，会提示 Unsupported）。

## metaData（解析后）

~~~json
{
  "name": "twoSum",
  "params": [
    {
      "name": "nums",
      "type": "integer[]"
    },
    {
      "name": "target",
      "type": "integer"
    }
  ],
  "return": {
    "type": "integer[]",
    "size": 2
  },
  "manual": false
}
~~~