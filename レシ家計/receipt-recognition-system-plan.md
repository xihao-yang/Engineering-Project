# 日本购物小票识别记账系统方案

## 1. 项目目标

做一个适合在日本日常生活中使用的小票识别记账系统，用来统计每天、每周、每个月的消费金额。

核心目标：

- 用 iPhone 15 快速拍小票；
- 不开发 iOS App；
- 不使用 Swift；
- 自动识别日本小票中的日期、店名、总金额、支付方式和分类；
- 支持手动确认和修改；
- 支持每日、每月、按店铺、按分类统计；
- 后期可导出 CSV / Excel。

第一版不建议追求完整商品明细识别。日本小票商品名、税率、折扣和店铺格式差异较大，先把总金额统计做稳更实用。

## 2. 推荐方案总览

最推荐的组合：

```text
iPhone 快捷指令 / LINE Bot / PWA
        ↓
Python FastAPI 后端
        ↓
OCR + AI 结构化提取
        ↓
SQLite / PostgreSQL
        ↓
统计查询 / CSV 导出
```

三种入口可以并存：

| 方案 | 适合场景 | 优点 | 缺点 |
| --- | --- | --- | --- |
| iPhone 快捷指令 | 最快拍照记账 | 不用打开 App，主屏幕一键拍小票 | 复杂校正体验一般 |
| LINE Bot | 聊天式记录 | 日本使用场景自然，发照片即可 | 需要配置 LINE Messaging API |
| PWA 网页应用 | 长期完整使用 | 有确认页、统计页、导出功能 | 需要打开网页或主屏幕 Web App |

实际建议：

1. 第一阶段：做 `iPhone 快捷指令 + FastAPI 后端`。
2. 第二阶段：加 `LINE Bot`。
3. 第三阶段：加 `PWA 统计后台`。

## 3. 系统命名建议

项目名推荐：

```text
レシ家計
```

含义接近 `receipt + 家计`，短，适合日本小票场景，也适合放在 iPhone 主屏幕和 LINE Bot 名称中。

其他备选：

- `小票账本`
- `レシート帳`
- `レシピタ`
- `円メモ`
- `今日いくら`
- `Receipt JP`
- `レシート家計簿`
- `Kakei Snap`

iPhone 快捷指令建议命名：

- `记小票`
- `查花费`

## 4. 第一版 MVP 功能

第一版只做最关键功能：

- 上传或拍摄小票图片；
- 自动识别日期；
- 自动识别店名；
- 自动识别总金额；
- 自动识别支付方式；
- 自动分类；
- 人工确认和修改；
- 保存到数据库；
- 查询今日消费；
- 查询本月消费；
- 按店铺统计；
- 按分类统计；
- CSV 导出。

暂缓功能：

- 商品级明细统计；
- 税率 8% / 10% 精细拆分；
- 预算提醒；
- 多用户系统；
- 银行卡或电子支付账单同步。

## 5. iPhone 快捷指令方案

### 5.1 使用体验

主屏幕放两个快捷指令：

```text
记小票
查花费
```

`记小票` 流程：

1. 打开快捷指令；
2. 自动调用相机拍照；
3. 压缩图片；
4. 上传到后端；
5. 后端识别小票；
6. 快捷指令显示识别结果；
7. 用户选择保存、修改金额或取消。

`查花费` 流程：

1. 打开快捷指令；
2. 选择 `今天`、`本月`、`上月`、`按分类`；
3. 调用后端统计接口；
4. 在 iPhone 上显示结果。

### 5.2 快捷指令动作设计

`记小票` 动作：

```text
拍照
  ↓
调整图像大小，宽度 1600 或 2000
  ↓
转换图像为 JPEG
  ↓
获取 URL 内容
  Method: POST
  URL: https://你的域名/api/receipts/scan
  Body: Form
    image: JPEG 图片
    timezone: Asia/Tokyo
  ↓
解析 JSON
  ↓
显示确认菜单
  保存 / 修改金额 / 取消
  ↓
确认保存时调用:
  POST https://你的域名/api/receipts/{receipt_id}/confirm
```

后端返回示例：

```json
{
  "receipt_id": "abc123",
  "store_name": "セブンイレブン",
  "date": "2026-06-29",
  "total_amount": 842,
  "payment_method": "PayPay",
  "category": "便利店",
  "confidence": 0.91
}
```

确认显示示例：

```text
セブンイレブン
2026-06-29
842円
分类：便利店

保存吗？
```

`查花费` 请求示例：

```text
GET https://你的域名/api/stats?range=month
```

返回显示示例：

```text
2026年6月
合计：58,420円
便利店：12,300円
超市：21,800円
餐饮：16,900円
交通：7,420円
```

### 5.3 为什么不建议纯快捷指令实现

纯快捷指令可以直接调用 OCR 或 AI API，并把结果写入 iCloud Drive CSV，但不适合长期使用：

- API Key 会保存在手机快捷指令里，不够安全；
- CSV 容易乱；
- 错误修正困难；
- 历史查询和统计会越来越麻烦；
- 后期扩展 LINE Bot 或网页后台不方便。

更合理的边界是：

```text
快捷指令负责拍照和确认；
后端负责 OCR、AI、数据库和统计。
```

## 6. LINE Bot 方案

### 6.1 使用体验

用户在 LINE 里给自己的 Bot 发小票照片：

```text
用户发送小票照片
  ↓
Bot 回复识别结果
  ↓
用户点击保存 / 修改 / 取消
  ↓
保存到数据库
```

Bot 回复示例：

```text
识别结果：
セブンイレブン
2026-06-29
842円
分类：便利店

保存吗？
[保存] [修改金额] [取消]
```

查询方式：

```text
今天
本月
上月
便利店
按分类
```

Bot 返回示例：

```text
今日支出：2,430円

セブンイレブン：842円
ライフ：1,188円
ドトール：400円
```

### 6.2 LINE Bot 系统结构

```text
iPhone LINE
   ↓ 发小票照片
LINE Messaging API
   ↓ webhook
FastAPI 后端
   ↓ 下载图片
OCR / OpenAI 识别
   ↓
SQLite / PostgreSQL
   ↓
LINE 回复统计结果
```

### 6.3 LINE Bot 技术点

需要使用 LINE Messaging API：

- webhook 接收消息；
- 验证 LINE 签名；
- 通过 `messageId` 下载图片；
- 用 reply message 回复识别结果；
- 用 quick reply 或 postback 做 `保存 / 修改 / 取消`；
- 尽量使用 Reply API，减少主动 Push 消息。

个人使用时，LINE 官方账号免费计划通常已经足够。设计上尽量让用户先发消息，然后 Bot 用 Reply API 回复。

## 7. PWA 网页方案

### 7.1 使用体验

在 iPhone Safari 打开网页后，添加到主屏幕，以后像 App 一样使用：

```text
主屏幕图标
  ↓
拍小票
  ↓
识别
  ↓
确认
  ↓
查看今日 / 本月统计
```

### 7.2 iPhone 拍照上传

网页上传按钮：

```html
<input type="file" accept="image/*" capture="environment">
```

这样在 iPhone 上会更自然地打开后置摄像头拍照。

### 7.3 PWA 优点

- 可以做完整确认页；
- 可以做统计仪表盘；
- 可以导出 CSV；
- 可以查看历史小票；
- 可以修改历史记录；
- 不需要 App Store；
- 不需要 Swift 或 iOS 原生开发。

## 8. OCR 与 AI 识别

### 8.1 OCR 选择

适合日本小票的 OCR：

- Google Cloud Vision OCR：支持 Japanese `ja`；
- Azure AI Vision Read OCR：支持日文；
- OpenAI Vision：可以直接从图片中理解文字和结构。

不建议首选 AWS Textract，因为它对日文和常见日本小票格式的适配不如前两者直接。

### 8.2 结构化提取

OCR 得到的是文本，还需要把文本转换成结构化数据。

建议使用：

```text
规则提取 + AI JSON 结构化输出
```

重点识别关键词：

- `合計`
- `小計`
- `税込`
- `税抜`
- `お預り`
- `お釣り`
- `領収書`
- `クレジット`
- `PayPay`
- `交通系IC`
- `現金`

结构化结果示例：

```json
{
  "date": "2026-06-29",
  "store_name": "セブンイレブン",
  "total_amount": 842,
  "tax_8": 0,
  "tax_10": 76,
  "payment_method": "PayPay",
  "category": "便利店",
  "items": [
    {
      "name": "おにぎり",
      "price": 138,
      "tax_rate": 8
    },
    {
      "name": "コーヒー",
      "price": 120,
      "tax_rate": 10
    }
  ]
}
```

第一版可以不保存 `items`，只保存总金额和分类。

## 9. 数据库设计

第一版 SQLite 就够，后期可换 PostgreSQL。

### 9.1 receipts 表

```sql
CREATE TABLE receipts (
  id TEXT PRIMARY KEY,
  image_path TEXT,
  store_name TEXT,
  purchase_date TEXT NOT NULL,
  total_amount INTEGER NOT NULL,
  payment_method TEXT,
  category TEXT,
  ocr_text TEXT,
  confidence REAL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### 9.2 receipt_items 表

```sql
CREATE TABLE receipt_items (
  id TEXT PRIMARY KEY,
  receipt_id TEXT NOT NULL,
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  tax_rate INTEGER,
  category TEXT,
  FOREIGN KEY (receipt_id) REFERENCES receipts(id)
);
```

### 9.3 categories 表，可选

```sql
CREATE TABLE categories (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  keywords TEXT
);
```

## 10. API 设计

### 10.1 扫描小票

```text
POST /api/receipts/scan
```

请求：

```text
multipart/form-data
image: file
timezone: Asia/Tokyo
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
  "confidence": 0.91,
  "needs_review": false
}
```

### 10.2 确认保存

```text
POST /api/receipts/{receipt_id}/confirm
```

请求：

```json
{
  "store_name": "セブンイレブン",
  "date": "2026-06-29",
  "total_amount": 842,
  "payment_method": "PayPay",
  "category": "便利店"
}
```

### 10.3 查询统计

```text
GET /api/stats?range=today
GET /api/stats?range=month
GET /api/stats?range=last_month
GET /api/stats?range=month&group_by=category
GET /api/stats?range=month&group_by=store
```

返回：

```json
{
  "range": "month",
  "currency": "JPY",
  "total": 58420,
  "groups": [
    {
      "name": "便利店",
      "amount": 12300
    },
    {
      "name": "超市",
      "amount": 21800
    }
  ]
}
```

## 11. 推荐技术栈

第一版：

- 后端：Python FastAPI
- 数据库：SQLite
- 图片存储：本地磁盘
- OCR：Google Cloud Vision 或 OpenAI Vision
- 结构化提取：OpenAI Structured Outputs / JSON Schema
- 入口：iPhone 快捷指令
- 部署：本地电脑、VPS、Railway、Render、Fly.io 均可

第二版：

- 数据库换 PostgreSQL；
- 增加 LINE Bot；
- 增加 PWA dashboard；
- 图片存储换 S3 / Cloudflare R2；
- 增加 CSV / Excel 导出。

## 12. 分类建议

第一版分类保持简单：

- 便利店
- 超市
- 餐饮
- 咖啡
- 药妆
- 日用品
- 交通
- 娱乐
- 医疗
- 其他

可以用店名关键词自动分类：

| 关键词 | 分类 |
| --- | --- |
| セブン, ローソン, ファミマ | 便利店 |
| ライフ, 西友, イオン, 業務スーパー | 超市 |
| マツキヨ, ウエルシア, ココカラ | 药妆 |
| ドトール, スタバ, タリーズ | 咖啡 |
| JR, 東京メトロ, PASMO, Suica | 交通 |

## 13. 开发阶段计划

### Phase 1：可用原型

- FastAPI 后端；
- SQLite 数据库；
- 上传图片接口；
- OCR / AI 识别；
- 保存小票；
- 今日 / 本月统计接口；
- iPhone 快捷指令接入。

### Phase 2：确认与修正

- 增加识别结果确认；
- 支持修改金额、店名、日期、分类；
- 增加错误日志；
- 增加历史记录查询。

### Phase 3：LINE Bot

- 配置 LINE Messaging API；
- webhook 接收图片；
- 下载用户发送的图片；
- 回复识别结果；
- 支持保存、修改、取消；
- 支持文字查询统计。

### Phase 4：PWA Dashboard

- 手机网页上传；
- 月度统计图；
- 分类占比；
- 店铺排行；
- 历史小票列表；
- CSV 导出。

## 14. 推荐最终形态

日常最顺手的组合：

```text
主屏幕快捷指令：记小票
主屏幕快捷指令：查花费
LINE Bot：补充聊天式记录
PWA：查看详细统计和修正历史
```

第一版先做：

```text
记小票快捷指令 + FastAPI + SQLite + OCR/AI + 今日/月度统计
```

这样成本最低，也最容易真正用起来。

## 15. 参考链接

- Apple Shortcuts User Guide: <https://support.apple.com/guide/shortcuts/welcome/ios>
- Apple Shortcuts Web APIs: <https://support.apple.com/guide/shortcuts/intro-to-web-apis-apd2d448b2de/ios>
- Apple Shortcuts JSON: <https://support.apple.com/guide/shortcuts/intro-to-using-json-apd0f2e057df/ios>
- Apple Add Shortcut to Home Screen: <https://support.apple.com/guide/shortcuts/add-a-shortcut-to-the-home-screen-apd735880972/ios>
- Apple Safari Web App Meta Tags: <https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariHTMLRef/Articles/MetaTags.html>
- LINE Messaging API: <https://developers.line.biz/en/docs/messaging-api/>
- LINE Receiving Messages: <https://developers.line.biz/en/docs/messaging-api/receiving-messages/>
- LINE Sending Messages: <https://developers.line.biz/en/docs/messaging-api/sending-messages/>
- LINE Quick Reply: <https://developers.line.biz/en/docs/messaging-api/using-quick-reply/>
- Google Cloud Vision OCR Languages: <https://cloud.google.com/vision/docs/languages>
- OpenAI Images and Vision: <https://platform.openai.com/docs/guides/images>
- OpenAI Structured Outputs: <https://platform.openai.com/docs/guides/structured-outputs>
