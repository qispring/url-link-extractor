# URL Link Extractor

从指定入口页面提取所有匹配URL前缀规则的链接，并获取每个链接对应网页的标题文本，实现网页链接与标题的批量采集。

## 功能简介

- 从入口页面HTML中解析所有 `<a>` 标签链接
- 按URL前缀/后缀规则过滤目标链接
- 并发请求各目标链接页面，提取 `<title>` 标题文本
- 支持UTF-8/GBK/GB2312等多种编码
- 结果输出为 `result.xlsx` Excel文件，包含URL和标题两列
- 支持重试、超时控制、robots.txt遵循等配置

## 安装方式

```bash
pip install -r requirements.txt
```

开发环境：

```bash
pip install -r requirements-dev.txt
pip install -e .
```

## 使用示例

### Python API

```python
from url_link_extractor import extract, ExtractRequest, ExtractConfig

request = ExtractRequest(
    url='https://support.huaweicloud.com/usermanual-cli/',
    prefix='https://support.huaweicloud.com/',
    suffix='.html',
    config=ExtractConfig(
        concurrency=5,
        timeout=30000,
        interval=500,
        retry_count=2,
        follow_robots_txt=False,
        max_links=1000,
        output_excel=True,
        output_path='result.xlsx',
    ),
)

def on_progress(progress):
    print(f'[{progress.completed}/{progress.total}] {progress.last_url} [{progress.last_status.value}]')

result = extract(request, on_progress)

print(f'统计: total={result.statistics.total}, success={result.statistics.success}, '
      f'failed={result.statistics.failed}, duration={result.statistics.duration}ms')

for item in result.results:
    print(f'  {item.url} -> {item.title} [{item.status.value}]')
```

### 命令行

```bash
python -m url_link_extractor https://support.huaweicloud.com/usermanual-cli/ \
    --prefix https://support.huaweicloud.com/ \
    --suffix .html \
    --concurrency 5 \
    --output result.xlsx
```

## 配置参数说明

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|------|------|--------|---------|------|
| concurrency | int | 5 | 1-20 | 并发请求数量 |
| timeout | int | 30000 | 1000-60000 | 请求超时（毫秒） |
| interval | int | 500 | 0-10000 | 请求间隔（毫秒） |
| retry_count | int | 2 | 0-5 | 最大重试次数 |
| follow_robots_txt | bool | False | - | 是否遵循robots.txt |
| max_links | int | 1000 | 1-10000 | 链接数量上限 |
| output_excel | bool | True | - | 是否导出Excel |
| output_path | str | result.xlsx | - | Excel输出路径 |

## 输出文件格式

`result.xlsx` 文件包含两列：
- **A列 - URL**：目标链接的完整URL地址
- **B列 - 标题**：对应网页的 `<title>` 标题文本

## 技术栈

- Python >= 3.8
- httpx（异步HTTP客户端）
- beautifulsoup4 + lxml（HTML解析）
- chardet（编码检测）
- openpyxl（Excel文件生成）
