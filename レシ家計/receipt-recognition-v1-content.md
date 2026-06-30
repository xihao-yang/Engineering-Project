# 日本购物小票识别记账系统第一版内容

## 1. 第一版定位

第一版目标是做一个能真实用于日常记账的最小可用版本。用户用 iPhone 15 拍摄日本购物小票，系统自动识别日期、店名、总金额、支付方式和消费分类，用户确认后保存，并可以查询今日和本月消费统计。

第一版不开发 iOS App，不使用 Swift，不做复杂商品明细统计。核心优先级是：拍照快、识别稳定、确认简单、统计可用。

## 2. 使用场景

### 2.1 记小票

用户在 iPhone 主屏幕点击 `记小票` 快捷指令，系统打开相机拍照。拍照后图片会被压缩并上传到后端，后端完成 OCR 和结构化识别，然后返回识别结果。

用户在手机上看到类似结果：

```text
セブンイレブン
2026-06-29
842円
支付方式：PayPay
分类：便利店

保存吗？
```

用户可以选择：

- 保存；
- 修改金额后保存；
- 取消。

### 2.2 查花费

用户在 iPhone 主屏幕点击 `查花费` 快捷指令，选择查询范围：

- 今天；
- 本月；
- 上月；
- 按分类。

系统返回类似结果：

```text
2026年6月
合计：58,420円

便利店：12,300円
超市：21,800円
餐饮：16,900円
交通：7,420円
```

## 3. 第一版功能范围

第一版必须包含：

- 小票图片上传；
- OCR 识别小票文字；
- AI 或规则提取结构化字段；
- 识别日期；
- 识别店名；
- 识别总金额；
- 识别支付方式；
- 自动分类；
- 用户确认保存；
- 用户修改金额后保存；
- SQLite 保存记录；
- 查询今日总消费；
- 查询本月总消费；
- 按分类统计；
- 按店铺统计；
- CSV 导出。

第一版暂不包含：

- 商品级明细统计；
- 8% / 10% 税率精细拆分；
- 预算提醒；
- 多用户账号；
- LINE Bot；
- PWA 后台；
- 银行卡或电子支付账单同步。

## 4. 系统组成

第一版由三部分组成：

```text
iPhone 快捷指令
  ↓
FastAPI 后端
  ↓
SQLite 数据库
```

快捷指令负责拍照、上传图片和显示确认结果。FastAPI 后端负责 OCR、AI 结构化提取、数据保存和统计查询。SQLite 负责本地持久化。

## 5. 快捷指令内容

### 5.1 记小票

快捷指令名称：`记小票`

动作流程：

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
保存时调用确认接口
```

### 5.2 查花费

快捷指令名称：`查花费`

动作流程：

```text
显示菜单
  今天 / 本月 / 上月 / 按分类
  ↓
调用统计接口
  ↓
格式化返回结果
  ↓
在 iPhone 弹窗显示
```

## 6. 需要识别的数据字段

每张小票第一版只保存以下字段：

| 字段 | 说明 | 示例 |
| --- | --- | --- |
| 日期 | 消费发生日期 | `2026-06-29` |
| 店名 | 小票上的店铺名称 | `セブンイレブン` |
| 总金额 | 实际支付金额，单位日元 | `842` |
| 支付方式 | 现金、信用卡、PayPay、交通系 IC 等 | `PayPay` |
| 分类 | 自动归类后的消费分类 | `便利店` |
| OCR 原文 | OCR 识别出的原始文本 | `合計 842円...` |
| 置信度 | 识别结果可信程度 | `0.91` |
| 状态 | 草稿、已确认、已取消 | `confirmed` |

## 7. 分类规则

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

自动分类优先使用店名关键词：

| 关键词 | 分类 |
| --- | --- |
| セブン, ローソン, ファミマ | 便利店 |
| ライフ, 西友, イオン, 業務スーパー | 超市 |
| マツキヨ, ウエルシア, ココカラ | 药妆 |
| ドトール, スタバ, タリーズ | 咖啡 |
| JR, 東京メトロ, PASMO, Suica | 交通 |

如果无法匹配关键词，则分类为 `其他`，用户后续可以手动修改。

## 8. API 内容

### 8.1 扫描小票

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

### 8.2 确认保存

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

返回：

```json
{
  "ok": true,
  "receipt_id": "abc123",
  "status": "confirmed"
}
```

### 8.3 查询统计

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

### 8.4 导出 CSV

```text
GET /api/receipts/export.csv?range=month
```

CSV 字段：

```text
date,store_name,total_amount,payment_method,category,created_at
```

## 9. 数据库内容

第一版使用 SQLite。

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

第一版可以先不创建 `receipt_items` 表。等后续需要商品级统计时再增加。

## 10. 识别逻辑

第一版识别流程：

```text
接收图片
  ↓
保存原图或压缩图
  ↓
调用 OCR / Vision 模型
  ↓
得到小票文本
  ↓
提取日期、店名、总金额、支付方式
  ↓
根据店名关键词自动分类
  ↓
返回待确认结果
```

金额识别优先级：

1. 优先识别 `合計` 后的金额；
2. 其次识别 `税込`、`お支払い金額`、`合計金額`；
3. 避免把 `お預り`、`お釣り` 误识别为总金额；
4. 无法确定时返回 `needs_review: true`。

## 11. 第一版验收标准

第一版完成时，应满足：

- iPhone 可以通过快捷指令拍照上传小票；
- 后端可以返回结构化识别结果；
- 用户可以确认保存；
- 用户可以修改金额后保存；
- SQLite 中可以看到已保存记录；
- 可以查询今日消费总额；
- 可以查询本月消费总额；
- 可以按分类查看本月统计；
- 可以导出本月 CSV；
- 识别失败时不会保存错误数据，而是提示需要人工确认。

## 12. 开发顺序

建议按以下顺序开发：

1. 初始化 FastAPI 项目；
2. 建立 SQLite 数据库和 `receipts` 表；
3. 实现图片上传接口；
4. 接入 OCR / Vision 识别；
5. 实现结构化字段提取；
6. 实现确认保存接口；
7. 实现统计接口；
8. 实现 CSV 导出；
9. 配置 iPhone 快捷指令；
10. 用真实日本小票测试并修正规则。

## 13. 第一版交付物

第一版交付内容包括：

- FastAPI 后端代码；
- SQLite 数据库初始化脚本；
- 小票扫描接口；
- 小票确认保存接口；
- 统计查询接口；
- CSV 导出接口；
- iPhone 快捷指令配置说明；
- 真实小票测试记录。
