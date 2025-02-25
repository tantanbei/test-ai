import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer
from threading import Thread

model_name = "deepseek-ai/deepseek-llm-7b-chat"
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")
model.generation_config = GenerationConfig.from_pretrained(model_name)
model.generation_config.pad_token_id = model.generation_config.eos_token_id

c = "提前还款后，期数减少和每期还款金额减少，哪个更好?"
print(c)
messages = [
    {"role": "user", "content": c}
]
input_tensor = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

# 设置流式输出的参数
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)

# 使用异步方式生成
generation_kwargs = dict(
    input_ids=input_tensor.to(model.device),
    max_new_tokens=10000,
    streamer=streamer,
    do_sample=True,
    temperature=0.7,
    top_p=0.95,
    repetition_penalty=1.3  # 添加重复惩罚
)

# 在新线程中运行生成
thread = Thread(target=model.generate, kwargs=generation_kwargs)
thread.start()

# 打印流式输出的结果
print("回答:", end=" ", flush=True)
for new_text in streamer:
    print(new_text, end="", flush=True)
print()