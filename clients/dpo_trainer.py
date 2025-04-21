from datasets import load_dataset
from trl import PPOConfig, PPOTrainer
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiopslab.orchestrator.tasks.analysis import AnalysisTask
from aiopslab.orchestrator.tasks.detection import DetectionTask
from aiopslab.orchestrator.tasks.localization import LocalizationTask
from aiopslab.orchestrator.tasks.mitigation import MitigationTask


def train(history):
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

    messages = [msg for msg in history if msg["role"] in ["user", "assistant"]]
    prompt_response_pairs = []

    for i in range(0, len(messages) - 1, 2):
        user_msg = messages[i]["content"]
        assistant_msg = messages[i + 1]["content"]
        prompt_response_pairs.append((user_msg, assistant_msg))

    final_result = history[-1] if isinstance(history[-1], dict) and "results" in history[-1] else {}
    score = final_result.get("results", {}).get("TTD", 0.0)  # Time to detect, as example reward
    success = final_result.get("final_state") == "VALID_SUBMISSION"


    # PPO Loop
    for prompt, response in prompt_response_pairs:
        query_tensor = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).input_ids.to(model.device)
        response_tensor = tokenizer(response, return_tensors="pt", truncation=True, padding=True).input_ids.to(model.device)

        reward = compute_reward(prompt, response)

        trainer.step([query_tensor], [response_tensor], [reward])

    print("PPO training complete.")




"""
prompts = []
prompts.append()

for prompt in prompts:
    
    response = ppo_trainer.generate(prompt)
    reward = compute_reward(response)  # 
    ppo_trainer.step([prompt], [response], [reward])
    
"""
    
    
    
    