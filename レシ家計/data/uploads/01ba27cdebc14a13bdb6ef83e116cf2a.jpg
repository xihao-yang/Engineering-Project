# 日本购物小票识别记账系统 MVP

这是根据 `receipt-recognition-system-plan.md` 和 `receipt-recognition-v1-content.md` 落地的第一版后端代码。

第一版范围：

- iPhone 快捷指令拍照上传；
- FastAPI 后端接收小票图片；
- OCR / Vision provider 可替换；
- 自动提取日期、店名、总金额、支付方式、分类；
- SQLite 保存草稿和确认记录；
- 今日、本月、上月统计；
- 按分类或店铺聚合；
- CSV 导出。

## 目录结构

```text
app/
  main.py        FastAPI 路由
  services.py    扫描、确认、统计、导出业务逻辑
  database.py    SQLite 表结构和查询
  parser.py      小票文本解析
  classifier.py  店名关键词分类
  ocr.py         mock / OpenAI Vision OCR provider
scripts/
  init_db.py     初始化数据库
tests/
  test_parser.py
  test_database.py
```

## 安装和启动

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000/docs
```

## 环境变量

复制 `.env.example` 为 `.env`，按需修改：

```text
RECEIPT_DB_PATH=data/receipts.sqlite3
RECEIPT_UPLOAD_DIR=data/uploads
RECEIPT_OCR_PROVIDER=mock
```

默认 `mock` provider 不会真正识别图片。它适合先打通接口和快捷指令流程：如果上传的是 UTF-8 文本，或请求里额外传了 `ocr_text`，系统会把它当作 OCR 文本解析。

要接 OpenAI Vision：

```text
RECEIPT_OCR_PROVIDER=openai
OPENAI_API_KEY=你的 API Key
OPENAI_MODEL=gpt-5.5
```

模型名称可以换成你账号可用的视觉模型。

## 初始化数据库

应用启动时会自动初始化数据库。也可以手动执行：

```powershell
python scripts/init_db.py
```

## API 示例

### 扫描小票

```text
POST /api/receipts/scan
multipart/form-data:
  image: file
  timezone: Asia/Tokyo
```

开发阶段可以传 `ocr_text` 直接测试解析：

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/receipts/scan `
  -F "image=@receipt.txt" `
  -F "timezone=Asia/Tokyo" `
  -F "ocr_text=セブンイレブン`n2026年6月29日`n合計 842円`nPayPay"
```

返回：

```json
{
  "receipt_id": "abc123",
  "store_name": "セブンイレブン",
  "date": "2026-06-29",
  "total_amount": 842,
  "payment_method": "PayPay",
  "category": "便利店",
  "confidence": 1.0,
  "needs_review": false
}
```

### 确认保存

```text
POST /api/receipts/{receipt_id}/confirm
```

```json
{
  "store_name": "セブンイレブン",
  "date": "2026-06-29",
  "total_amount": 842,
  "payment_method": "PayPay",
  "category": "便利店"
}
```

### 查询统计

```text
GET /api/stats?range=today
GET /api/stats?range=month
GET /api/stats?range=last_month
GET /api/stats?range=month&group_by=category
GET /api/stats?range=month&group_by=store
```

### 导出 CSV

```text
GET /api/receipts/export.csv?range=month
```

## 下一步

第一版后续最值得补的是：

- 用真实日本小票样本微调 `app/parser.py` 的金额识别规则；
- 给 iPhone 快捷指令写图文配置说明；
- 增加一个简单 PWA 确认页，替代快捷指令里的复杂确认菜单；
- 根据实际使用成本选择 OpenAI Vision 或 Google Cloud Vision。
