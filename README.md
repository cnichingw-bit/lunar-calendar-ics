# 🌙 阴阳历择日日历 - macOS日历订阅源

将每日的干支、宜忌、吉凶神自动同步到macOS日历。**一次订阅，永久同步。**

![version](https://img.shields.io/badge/version-1.0.0-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## ✨ 功能特性

- 📅 **实时数据同步**：每24小时自动更新一次
- 🔄 **跨设备同步**：Mac、iPhone、iPad、Outlook、Google Calendar都支持
- 📱 **零安装**：只需一个订阅URL，无需下载App
- 🎨 **智能颜色标记**：
  - 🔴 **红色**：包含天德/月德等吉神的日子
  - ⚪ **灰色**：包含月破/日值四离/四绝的日子
- 📋 **完整信息显示**：
  - 标题：日期 + 日干支
  - 描述：月干支、宜、忌、吉凶神

---

## 🚀 快速开始

### 1️⃣ 方案A：使用现成的订阅源（推荐）

如果您不想自己部署，可以直接使用我们生成的文件。

#### 在macOS日历中添加订阅：

1. **打开"日历"应用**

2. **菜单 → 文件 → 新建日历订阅**

3. **粘贴以下URL之一**：
   ```
   https://[您的GitHub用户名].github.io/lunar_calendar_2024_2026.ics
   ```
   
   或者（3年合并版）：
   ```
   https://[您的GitHub用户名].github.io/lunar_calendar_2024_01_to_2026_12.ics
   ```

4. **点击"订阅"** → 完成！

#### 或者在iPhone/iPad中：

1. 打开 **设置 → 日历**
2. 点击 **添加日历 → 订阅日历**
3. 粘贴上述URL
4. 点击 **添加**

---

### 2️⃣ 方案B：自己部署（推荐有服务器的用户）

#### 前置要求

- Python 3.11+
- 一个GitHub账户（用于免费托管和自动化）
- 可选：服务器或云存储（用于自托管）

#### 部署步骤

##### Step 1: Fork或克隆此仓库

```bash
# 克隆到本地
git clone https://github.com/[您的用户名]/lunar-calendar-ics.git
cd lunar-calendar-ics
```

##### Step 2: 配置本地环境

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

##### Step 3: 本地测试生成ICS文件

```bash
# 生成2024年1月到2025年12月的日历
python lunar_calendar_to_ics.py 2024 1 2025 12

# 或生成单年日历
python lunar_calendar_to_ics.py 2024 1 2024 12
```

输出：
```
🗓️  开始生成日历：2024-01-01 → 2025-12-31
📅 总天数：730天

⏳ 处理 2024-01-01... ✓ (甲辰)
⏳ 处理 2024-01-02... ✓ (乙巳)
...
✅ ICS文件已保存：lunar_calendar_2024_01_to_2025_12.ics
```

##### Step 4: 推送到GitHub并启用GitHub Pages

```bash
# 如果有新的ICS文件
git add *.ics
git commit -m "Add lunar calendar ICS files"
git push origin main
```

##### Step 5: 启用GitHub Pages

1. 进入你的GitHub仓库
2. **Settings → Pages**
3. **Source** 选择 **Deploy from a branch**
4. **Branch** 选择 **main**，目录选择 **/(root)**
5. 点击 **Save**

GitHub Pages会在几分钟后启动。您的ICS文件将可以在以下URL访问：

```
https://[您的GitHub用户名].github.io/lunar_calendar_2024_01_to_2025_12.ics
```

##### Step 6: 启用自动化更新（可选）

如果您想每天自动更新日历：

1. **Settings → Actions → General**
2. **Workflow permissions** 选择 **Read and write permissions**
3. 工作流会在每天UTC 0点（北京时间8点）自动运行

---

## 📖 详细说明

### ICS文件格式

生成的ICS文件包含以下信息：

```
事件标题：01/01 甲子
事件描述：
【月干支】癸丑月
【宜】祭祀、祈福、开业
【忌】动土、破土
【吉神】天德、月德
【凶神】/

颜色标签：RED（含吉神）
```

### 颜色标记规则

| 标签 | 颜色 | 条件 | 优先级 |
|------|------|------|--------|
| 吉神 | 🔴 RED | 包含天德、月德等吉神 | 2 |
| 凶神 | ⚪ GRAY | 包含月破、日值四离/四绝 | 1（优先） |
| 默认 | - | 无特殊标记 | - |

### API参数说明

脚本调用的API格式：

```
GET https://w.yxs.bj.cn/Index/Zeri/q

参数：
- mo: api （固定）
- token: 05dba5a3fc088c9781ebc24fb65a1ec6 （固定）
- type: time （固定）
- time_yinyang: 阳历 （固定）
- time_year: 2024 （年）
- time_month: 1 （月）
- time_day: 15 （日）
- time_hour: 0 （小时，固定）
- time_min: 0 （分钟，固定）
- time_run: 0 （固定）
```

API返回的JSON数据包含：
```json
{
  "result": {
    "ganzhi_day": "甲子",        // 日干支
    "ganzhi_month": "癸丑月",    // 月干支
    "yi": "祭祀、祈福、开业",     // 宜
    "ji": "动土、破土",           // 忌
    "jishen": "天德、月德",       // 吉神
    "xiongshen": "月破",          // 凶神
    ...
  }
}
```

---

## 📱 在macOS日历中使用

### 添加订阅

1. **打开日历应用**
2. **菜单 → 文件 → 新建日历订阅**
3. **粘贴ICS订阅URL**
4. **点击订阅**

### 查看事件

- 事件标题显示：**日期 + 日干支**
- 事件详情显示：**宜、忌、吉凶神**
- **侧边栏**显示颜色标签（红/灰）

### 自动刷新

- macOS日历会每24小时自动刷新一次
- 或手动右键点击日历名称 → **刷新**

---

## 🔧 高级配置

### 自定义时间范围

如果要生成特定时间段的日历：

```bash
# 生成2025年的日历
python lunar_calendar_to_ics.py 2025 1 2025 12

# 生成2024年6月到2025年6月
python lunar_calendar_to_ics.py 2024 6 2025 6
```

### 在自己的服务器上托管

如果不使用GitHub Pages，可以：

1. 将生成的`.ics`文件上传到自己的服务器
2. 配置服务器支持HTTP范围请求（某些日历应用需要）
3. 获得CORS跨域支持

**Nginx配置示例**：
```nginx
server {
    listen 80;
    server_name calendar.example.com;

    location / {
        root /var/www/calendar;
        
        # 添加正确的Content-Type
        types {
            text/calendar ics;
        }
        
        # 支持范围请求
        default_type application/octet-stream;
        
        # CORS支持
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, HEAD, OPTIONS';
    }
}
```

### 定时更新脚本（本地服务器）

**cron配置示例** `crontab -e`：

```cron
# 每天早上8点更新日历
0 8 * * * /usr/bin/python3 /path/to/lunar_calendar_to_ics.py 2024 1 2026 12 && cp /path/to/*.ics /var/www/calendar/
```

---

## 🛠️ 故障排除

### 问题1：ICS文件无法订阅

**症状**：日历提示"无法添加日历"

**解决**：
- ✅ 确认URL正确（没有多余空格）
- ✅ 确认服务器返回正确的Content-Type：`text/calendar`
- ✅ 试试GitHub Pages的其他缓存：清空浏览器缓存

### 问题2：颜色标签不显示

**症状**：事件没有红色/灰色标签

**解决**：
- ⚠️ macOS日历对颜色支持有限
- ✅ 可以在日历设置中手动为日历设置颜色
- ✅ 或在事件详情中查看"分类"字段

### 问题3：事件信息不完整

**症状**：看不到宜忌信息

**解决**：
- ✅ 在日历中双击事件打开详情
- ✅ 确认"描述"字段有内容
- ✅ 某些日历应用的显示方式不同，可以尝试其他应用

### 问题4：数据延迟或不准确

**症状**：日期的数据与官方不符

**解决**：
- ⚠️ 源API可能有延迟
- ✅ 可以手动运行脚本重新生成
- ✅ 检查API是否返回数据（可在浏览器中测试URL）

---

## 📊 项目结构

```
lunar-calendar-ics/
├── lunar_calendar_to_ics.py      # 核心脚本
├── requirements.txt               # Python依赖
├── .github/
│   └── workflows/
│       └── generate-calendar.yml  # GitHub Actions自动化
├── *.ics                          # 生成的日历文件
└── README.md                      # 本说明文档
```

---

## 🔐 隐私和安全

- ✅ 所有处理都在本地进行（或GitHub Action中）
- ✅ 不存储任何个人信息
- ✅ API调用使用公开Token（源自官方）
- ✅ ICS文件是公开的日历数据，无隐私风险

---

## 📝 常见问题

### Q: 是否支持其他日历应用？
A: 是的！支持任何兼容ICS标准的日历应用：
- ✅ macOS 日历
- ✅ iOS 日历
- ✅ Outlook
- ✅ Google Calendar
- ✅ Mozilla Thunderbird
- ✅ 大多数第三方日历应用

### Q: 可以自定义事件内容吗？
A: 可以。编辑 `format_event_description()` 方法来修改显示的信息。

### Q: 订阅源会一直更新吗？
A: 是的，GitHub Actions会每天自动执行，保持ICS文件最新。

### Q: 如何删除订阅？
A: 在日历应用中右键点击日历 → 删除，或在设置中取消订阅。

---

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 许可证

MIT License - 自由使用和修改

---

## 📞 联系方式

如有问题或建议，欢迎反馈！

---

**祝您使用愉快！** 🎉

*最后更新：$(date)*
