"""
AI Token 优化工具集
提供精确计数、截断、对话历史压缩等功能。
"""

import tiktoken
from typing import List, Dict


def _get_encoding(model: str):
    """尝试获取模型对应的编码，失败则回退到 cl100k_base。"""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """计算文本的 Token 数量。"""
    enc = _get_encoding(model)
    return len(enc.encode(text))


def count_message_tokens(messages: List[Dict[str, str]], model: str = "gpt-4") -> int:
    """
    粗略估算消息列表的 Token 总数。
    注意：这里只计算 content 字段，实际 API 会有额外格式 Token，
    但该方法对压缩和比较已足够。
    """
    return sum(count_tokens(m["content"], model) for m in messages)


def truncate_text(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """将文本截断到指定 Token 数以内。"""
    if max_tokens <= 0:
        return ""
    enc = _get_encoding(model)
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens])


def compress_history(
    messages: List[Dict[str, str]],
    max_tokens: int,
    model: str = "gpt-4"
) -> List[Dict[str, str]]:
    """
    压缩对话历史，保证总 Token 数不超过 max_tokens。
    优先保留 system 消息，然后从最后一条消息向前保留。
    如果单条消息过长，会尝试截断它以填满剩余配额。
    """
    if not messages:
        return []

    system_msgs = []
    other_msgs = []

    for m in messages:
        if m["role"] == "system":
            system_msgs.append(m)
        else:
            other_msgs.append(m)

    kept = []
    current_tokens = sum(count_tokens(m["content"], model) for m in system_msgs)
    # 如果 system 消息本身已超限，则强制截断最后一条 system 消息
    if current_tokens > max_tokens and system_msgs:
        # 只保留第一条，并截断
        sys_content = system_msgs[0]["content"]
        truncated_sys = truncate_text(sys_content, max_tokens, model)
        return [{"role": "system", "content": truncated_sys}]

    kept = system_msgs[:]  # 保留所有 system 消息

    # 从最新的非系统消息开始向前保留
    for m in reversed(other_msgs):
        msg_tokens = count_tokens(m["content"], model)
        if current_tokens + msg_tokens <= max_tokens:
            kept.insert(len(system_msgs), m)  # 保持时间顺序：系统消息后是较早消息
            current_tokens += msg_tokens
        else:
            # 尝试部分保留
            remaining = max_tokens - current_tokens
            if remaining > 10:  # 至少保留 10 token 才有意义
                truncated_content = truncate_text(m["content"], remaining, model)
                truncated_msg = {"role": m["role"], "content": truncated_content}
                kept.insert(len(system_msgs), truncated_msg)
                current_tokens += count_tokens(truncated_content, model)
            break  # 无法再容纳更早的消息

    return kept


if __name__ == "__main__":
    # 简单自测
    msgs = [
        {"role": "system", "content": "你是一个简洁的助手。"},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，有什么可以帮你的？"},
        {"role": "user", "content": "讲一个长篇故事" * 50},  # 模拟长消息
    ]
    compressed = compress_history(msgs, max_tokens=100)
    print("压缩后消息数:", len(compressed))
    print("总 Token:", count_message_tokens(compressed))