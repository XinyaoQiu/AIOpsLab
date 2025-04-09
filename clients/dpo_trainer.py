from datasets import load_dataset
from trl import PPOConfig, PPOTrainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
train_dataset = load_dataset("", split="train")

config = PPOConfig(
    model_name=model_name,
    learning_rate=1.41e-5,
    batch_size=16,
    log_with=None,  # or "wandb"
    mini_batch_size=4
)

trainer = PPOTrainer(config=config, model=model, tokenizer=tokenizer)

prompts = []

for prompt in prompts:
    
    response = ppo_trainer.generate(prompt)
    reward = compute_reward(response)  # 
    ppo_trainer.step([prompt], [response], [reward])