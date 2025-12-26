const fs = require('fs');
const path = require('path');

const LANGUAGE_MAP = {
  '.java': 'Java',
  '.rs': 'Rust',
  '.go': 'Go',
  '.py': 'Python'
};

const DIFFICULTY_MAP = {
  '0001-two-sum': ['Easy', 'Two Sum'],
  '0002-add-two-numbers': ['Medium', 'Add Two Numbers'],
  '0015-3sum': ['Medium', '3Sum'],
  '0042-trapping-rain-water': ['Hard', 'Trapping Rain Water'],
  // 你可以继续在这里添加常见题目，后续我们再升级为 API 自动获取
};

const problems = [];
const languageStats = { Java: 0, Rust: 0, Go: 0, Python: 0 };
let total = 0, easy = 0, medium = 0, hard = 0;

const folders = fs.readdirSync('.')
  .filter(f => fs.statSync(f).isDirectory() && /^\d{4}-/.test(f));
folders.sort();

for (const folder of folders) {
  const number = folder.slice(0, 4);
  const slug = folder.slice(5);

  const mapEntry = DIFFICULTY_MAP[folder] || [];
  const difficulty = mapEntry[0] || 'Unknown';
  const title = mapEntry[1] || slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  const files = fs.readdirSync(folder);
  const supportedLangs = [];

  for (const file of files) {
    if (file.startsWith('solution.')) {
      const ext = path.extname(file);
      const lang = LANGUAGE_MAP[ext];
      if (lang) {
        supportedLangs.push(lang);
        languageStats[lang]++;
      }
    }
  }

  if (supportedLangs.length > 0) {
    const mtime = fs.statSync(folder).mtime;
    const date = `${mtime.getFullYear()}-${String(mtime.getMonth() + 1).padStart(2, '0')}-${String(mtime.getDate()).padStart(2, '0')}`;

    problems.push({
      number,
      title,
      link: `https://leetcode.com/problems/${slug}/`,
      difficulty,
      langs: supportedLangs.sort().join(', '),
      date
    });

    total++;
    if (difficulty === 'Easy') easy++;
    else if (difficulty === 'Medium') medium++;
    else if (difficulty === 'Hard') hard++;
  }
}

// 生成表格
let table = '| 编号 | 标题 | 难度 | 支持语言 | 更新时间 |\n';
table += '|------|------|------|----------|----------|\n';
for (const p of problems) {
  table += `| ${p.number} | [${p.title}](${p.link}) | ${p.difficulty} | ${p.langs} | ${p.date} |\n`;
}

// 生成新内容
const newContent =
  `## 刷题进度\n\n` +
  `- 已解决题目：${total}\n` +
  `- Easy：${easy}\n` +
  `- Medium：${medium}\n` +
  `- Hard：${hard}\n\n` +
  `## 语言统计\n\n` +
  `- Java：${languageStats.Java} 题\n` +
  `- Rust：${languageStats.Rust} 题\n` +
  `- Go：${languageStats.Go} 题\n` +
  `- Python：${languageStats.Python} 题\n\n` +
  `## 题目列表\n\n` +
  table;

// 读取并更新 README
let readme = fs.readFileSync('README.md', 'utf-8');

const startMarker = '## 刷题进度';
const endMarker = '## 其他';

const start = readme.indexOf(startMarker);
const end = readme.indexOf(endMarker);

if (start !== -1 && end !== -1) {
  readme = readme.slice(0, start) + newContent + '\n\n' + readme.slice(end);
} else {
  readme += '\n' + newContent;
}

fs.writeFileSync('README.md', readme);

console.log('README updated successfully!');
