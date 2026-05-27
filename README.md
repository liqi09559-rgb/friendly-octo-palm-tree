# 🧠 AI Token Saver — 降低 AI Token 用量的实战技能集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 一个面向 LLM 开发者与重度用户的技能集合，帮助你在与 GPT-4、Claude 等模型交互时，**系统性减少 Token 消耗**，直接降低 API 成本、缩短响应时间。

---

ai-token-saver/
├── README.md
├── .gitignore
├── LICENSE
├── requirements.txt
└── token saver.skill.py

---

## ✨ 核心技能

- 🎯 **精简 Prompt 设计** — 去除冗余，保留核心指令
- 🧹 **对话上下文压缩** — 自动裁剪历史消息，只保留关键信息
- 📉 **强制简洁输出** — 限制回答长度，减少生成 Token
- 🔁 **缓存与前缀复用** — 利用固定系统消息节省输入 Token
- 📊 **实时 Token 计数与预警** — 在代码层面监测与控制用量
- 🧩 **长文本预处理** — 分块、摘要后再送入模型

---
安装依赖：pip install -r requirements.txt

---

## 📚 技能详解
1. 精简系统提示（System Prompt）
  反例（浪费 Token）：

"你是一个友好、知识渊博、有耐心、善于倾听的助手，能够以清晰且详细的方式回答各种问题，并且在不确定时会如实告知……"

正例：

"You are a helpful assistant. Answer concisely."

📌 去掉修饰语，把行为指令化。每条固定提示消耗的 Token × 调用次数 = 巨额开销。

2. 对话历史瘦身
  长对话是 Token 大户典型策略：

--只保留最近 N 轮 对话

--对更早的历史进行 自动摘要，用一句概括替代原始消息

--利用 token_optimizer.compress_history() 按 Token 上限自动裁剪
如果希望保留更早的语义，可先调用另一个轻量模型生成摘要，再拼到新 system prompt 中。

3. 文本预处理压缩
  在将用户提供的长文档送入模型前：

--去除多余空行、无意义装饰符

--提取核心段落（如使用关键词匹配、BM25）

--将长文本拆分成多个小块，配合递归摘要

4. 强制简洁输出
  在 Prompt 末尾明确要求：

"Answer in one sentence."
"Reply with JSON only, no explanation."
5. 利用 Prompt Caching（前缀复用）
  如果你的系统提示和固定前缀长时间不变，请：

--保持它们在最前面

--使用支持前缀缓存的平台（如 Anthropic 的 Prompt Caching、OpenAI 对相同前缀的自动缓存）

--避免在动态内容前插入变化的字段（如时间戳）

--技巧：把工具定义、角色描述放在前面，动态用户消息放在最后。

6. 分块处理长文
   分块策略：

--按段落或固定 Token 数切分

--逐块提取关键信息，再汇总

--使用 Map-Reduce / Refine 模式

7. 选择合适的模型与参数
  简单任务用 gpt-3.5-turbo 替代 gpt-4

非创造性任务将 temperature 设为 0，减少随机性，有时生成更短

关闭不必要的功能（如 function calling）以减少提示 Token

----

## 🧪 最佳实践检查清单
-系统提示是否少于 200 Token？

-是否每次请求都发送了完整历史？是否可只发送摘要 + 最近 N 轮？

-输出是否限制了 max_tokens？

-长文档是否提前分块或摘要？

-是否复用了固定前缀以利用缓存？

-是否在简单任务上使用了过强的模型？

----

## 📖 完整示例
python
from token_optimizer import compress_history, count_message_tokens

conversation = [
    {"role": "system", "content": "You are a code reviewer."},
    {"role": "user", "content": "Review this code: ..."},
    {"role": "assistant", "content": "The code has issues..."},
    {"role": "user", "content": "Can you explain more?"},
    # 模拟大量历史...
]

print(f"原始 Token 数: {count_message_tokens(conversation)}")

compressed = compress_history(conversation, max_tokens=600)
print(f"压缩后 Token 数: {count_message_tokens(compressed)}")

-----

## 🛠️ 工具脚本说明
token_optimizer.py 提供了以下函数：
函数	功能
count_tokens(text, model)	计算单段文本 Token 数
count_message_tokens(messages, model)	计算消息列表总 Token 数
truncate_text(text, max_tokens, model)	按 Token 数截断文本
compress_history(messages, max_tokens, model)	自动裁剪对话历史，保留 system 消息并从最新消息向前填充

----

## 📄 许可证
本项目采用 MIT License。欢迎贡献更多 Token 优化技巧。
如果帮你省了成本，请给个 ⭐ Star 支持一下！
