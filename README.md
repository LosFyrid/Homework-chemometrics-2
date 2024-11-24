# 化学计量学论文显著性分析工具

这是一个用于批量分析学术论文中统计显著性的自动化工具。该工具可以自动下载论文、提取相关内容、判断统计显著性并进行数据分析,帮助研究人员快速了解大量论文中的统计显著性结果。

## 主要功能

- 自动下载论文PDF(支持开放获取和Sci-Hub)
- PDF转文本解析
- 基于关键词的相关内容提取
- 使用GPT-4o进行显著性判断
- 统计显著性结果分析

## 工作流程

1. 从Excel文件读取论文元数据(DOI、标题等)
2. 通过Unpaywall API和Sci-Hub自动下载论文PDF
3. 使用PyMuPDF将PDF转换为文本
4. 提取包含显著性相关内容(p值、显著性检验等)的段落
5. 使用GPT-4判断每篇论文的统计显著性
6. 进行统计分析并生成JSON格式报告

## 安装配置

### 环境要求
- Python 3.7+
- OpenAI API密钥(用于GPT-4o)
- 有效的邮箱地址(用于Unpaywall API)

### 依赖包
- pandas: 数据处理
- requests: 网络请求
- pymupdf: PDF解析
- beautifulsoup4: 网页解析
- dspy: GPT接口调用
- python-dotenv: 环境变量管理

### 配置步骤

1. 克隆仓库:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量:
   - 创建一个`.env`文件，并添加以下内容：
     ```
     OPENAI_API_KEY=your_openai_api_key
     EMAIL=your_email_for_unpaywall
     ```

## 使用说明

1. 将论文元数据Excel文件(metadata.xls)替换到项目根目录。如果使用Web of Science导出，请在导出设置包括"Title", "Source"和"Times Cited Count"，否则，文件需包含以下列:
   - DOI: 论文的DOI标识符
   - Article Title: 论文标题
   - Times Cited, All Databases: 引用次数
2. 运行主程序:
   ```bash
   python main.py
   ```
3. 相关内容提取结果将保存在`related_content.json`文件中，显著性判断结果将保存在`significance_results.json`文件中。显著性结果统计输出在控制台。
