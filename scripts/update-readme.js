
const fs = require('fs');
const path = require('path');

// --- 配置区域 ---
const LANGUAGE_MAP = {
    '.java': 'Java',
    '.rs': 'Rust',
    '.go': 'Go',
    '.py': 'Python',
    '.cpp': 'C++',
    '.c': 'C',
    '.js': 'JavaScript',
    '.ts': 'TypeScript'
};

// 难度等级权重，用于排序或统计
const DIFFICULTY_LEVEL = {
    'Easy': 1,
    'Medium': 2,
    'Hard': 3,
    'Unknown': 4
};

// --- 核心逻辑 ---

const problems = [];
const languageStats = {}; // 动态统计: { 'Python': 10, 'Rust': 5 }
const difficultyStats = { 'Easy': 0, 'Medium': 0, 'Hard': 0, 'Unknown': 0 };
let total = 0;

// 1. 扫描所有题目目录 (格式: 0001-two-sum)
const folders = fs.readdirSync('.')
    .filter(f => fs.statSync(f).isDirectory() && /^\d{4}-/.test(f));

folders.sort();

for (const folder of folders) {
    const number = folder.slice(0, 4);
    const slug = folder.slice(5);
    
    // --- 动态获取元数据 (从 problem.md) ---
    let title = slug;
    let difficulty = 'Unknown';
    let link = `https://leetcode.cn/problems/${slug}/`;

    const mdPath = path.join(folder, 'problem.md');
    if (fs.existsSync(mdPath)) {
        const content = fs.readFileSync(mdPath, 'utf-8');
        
        // 解析标题: # 1. Two Sum
        const titleMatch = content.match(/^# \d+\.\s+(.+)$/m);
        if (titleMatch) title = titleMatch[1].trim();

        // 解析难度: 难度：Easy / Difficulty: Hard
        let diffMatch = content.match(/(?:难度|Difficulty|Diff)[:：]\s*(\w+)/i);
        let rawDiff = diffMatch ? diffMatch[1] : null;

        // 方案 B：如果没找到前缀，或者找到的不是难度词，就去前 5 行暴力搜关键字
        if (!rawDiff || !['easy', 'medium', 'hard', '简单', '中等', '困难'].includes(rawDiff.toLowerCase())) {
            // 只看前 500 个字符，防止匹配到正文里的单词
            const head = content.slice(0, 500).toLowerCase();
            if (head.includes('easy') || head.includes('简单')) rawDiff = 'Easy';
            else if (head.includes('medium') || head.includes('中等')) rawDiff = 'Medium';
            else if (head.includes('hard') || head.includes('困难')) rawDiff = 'Hard';
        }

        // 统一标准化
        if (rawDiff) {
            const low = rawDiff.toLowerCase();
            if (['easy', '简单'].includes(low)) difficulty = 'Easy';
            else if (['medium', '中等'].includes(low)) difficulty = 'Medium';
            else if (['hard', '困难'].includes(low)) difficulty = 'Hard';
        }
    }

    // --- 扫描代码文件 ---
    const files = fs.readdirSync(folder);
    const supportedLangs = [];

    for (const file of files) {
        // 只识别 solution.xxx 文件
        if ((file.startsWith('solution.') || file.startsWith('Solution.')) && file !== 'solution.pyc') {
            const ext = path.extname(file);
            const langName = LANGUAGE_MAP[ext];
            
            if (langName) {
                supportedLangs.push(langName);
                // 动态统计语言数量
                languageStats[langName] = (languageStats[langName] || 0) + 1;
            }
        }
    }

    // 只有当该目录下存在代码解法时，才计入列表
    if (supportedLangs.length > 0) {
        // 获取最后修改时间 (取 solution 文件的最新时间)
        // 简单起见，取文件夹修改时间，或者取最新的代码文件时间
        let lastMod = fs.statSync(folder).mtime;
        
        // 格式化日期 YYYY-MM-DD
        const date = lastMod.toISOString().split('T')[0];

        problems.push({
            number,
            title,
            link,
            difficulty,
            langs: supportedLangs.sort().join(', '),
            date
        });

        total++;
        difficultyStats[difficulty] = (difficultyStats[difficulty] || 0) + 1;
    }
}

// --- 生成 Markdown 内容 ---

// 1. 概览统计
let statsContent = `## 刷题进度\n\n`;
statsContent += `- 🏁 **已解决题目**：${total}\n`;
statsContent += `- 🟢 **Easy**：${difficultyStats.Easy}\n`;
statsContent += `- 🟡 **Medium**：${difficultyStats.Medium}\n`;
statsContent += `- 🔴 **Hard**：${difficultyStats.Hard}\n\n`;

// 2. 语言统计 (按数量降序排列)
statsContent += `### 语言分布\n\n`;
const sortedLangs = Object.entries(languageStats).sort((a, b) => b[1] - a[1]);
if (sortedLangs.length === 0) {
    statsContent += `_暂无数据_\n\n`;
} else {
    statsContent += `| 语言 | 题数 |\n|:---|:---:|\n`;
    for (const [lang, count] of sortedLangs) {
        statsContent += `| ${lang} | ${count} |\n`;
    }
    statsContent += `\n`;
}

// 3. 详细题目表格
let tableContent = `## 题目列表\n\n`;
tableContent += `| 编号 | 标题 | 难度 | 解法 | 更新时间 |\n`;
tableContent += `|:---:|:-----|:---:|:-----|:--------:|\n`;

for (const p of problems) {
    // 难度图标美化
    let diffIcon = '';
    if (p.difficulty === 'Easy') diffIcon = '🟢';
    else if (p.difficulty === 'Medium') diffIcon = '🟡';
    else if (p.difficulty === 'Hard') diffIcon = '🔴';
    
    tableContent += `| ${p.number} | [${p.title}](${p.link}) | ${diffIcon} ${p.difficulty} | ${p.langs} | ${p.date} |\n`;
}

const finalContent = statsContent + tableContent;

// --- 写入 README.md ---
const readmePath = 'README.md';
let readme = '';

if (fs.existsSync(readmePath)) {
    readme = fs.readFileSync(readmePath, 'utf-8');
} else {
    // 如果文件不存在，创建基础模板
    readme = `# LeetCode Solutions\n\nMy LeetCode journey.\n\n<!-- START_PROBLEMS -->\n<!-- END_PROBLEMS -->\n`;
}

// 使用标记替换内容
const startMarker = '<!-- START_PROBLEMS -->';
const endMarker = '<!-- END_PROBLEMS -->';

const startIndex = readme.indexOf(startMarker);
const endIndex = readme.indexOf(endMarker);

if (startIndex !== -1 && endIndex !== -1) {
    readme = readme.slice(0, startIndex + startMarker.length) + 
             '\n\n' + finalContent + '\n' + 
             readme.slice(endIndex);
    fs.writeFileSync(readmePath, readme);
    console.log('✅ README updated successfully with dynamic data!');
} else {
    console.warn('⚠️ Markers not found. Appending content to the end.');
    fs.appendFileSync(readmePath, `\n\n${startMarker}\n\n${finalContent}\n${endMarker}`);
}
