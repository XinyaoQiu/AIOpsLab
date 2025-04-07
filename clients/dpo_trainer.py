from datasets import load_dataset
from trl import DPOConfig, DPOTrainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
train_dataset = load_dataset("", split="train")

training_args = DPOConfig(output_dir="Qwen2-0.5B-DPO", logging_steps=10, bf16=True)

trainer = DPOTrainer(model=model, args=training_args, processing_class=tokenizer, train_dataset=train_dataset)
print("about to train!")
trainer.train()
