from datasets import load_dataset
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import os
import sys
from copy import deepcopy
from datasets import Dataset


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def train(history):
    
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
    tokenizer.pad_token = tokenizer.eos_token
    
    base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
    generation_config = base_model.generation_config
    
    model = AutoModelForCausalLMWithValueHead.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
    model.generation_config = generation_config


    messages = []

    for msg in history:
        
        if 'role' in msg:
            if msg['role'] == "user" or msg['role'] == "assistant":
                messages.append(msg)
            

    prompt_response_pairs = []

    for i in range(0, len(messages) - 1, 2):
        user_msg = messages[i]["content"]
        assistant_msg = messages[i + 1]["content"]
        prompt_response_pairs.append((user_msg, assistant_msg))

    final_result = history[-1] if isinstance(history[-1], dict) and "results" in history[-1] else {}
    score = final_result.get("results", {}).get("score", 0.0)  # Time to detect, as example reward
    success = final_result.get("final_state") == "VALID_SUBMISSION"
    
    train_dataset = Dataset.from_dict({
        "prompt": [p for p, _ in prompt_response_pairs]
    })


    config = PPOConfig(
        learning_rate=1.41e-5,
        mini_batch_size=4,
        gradient_accumulation_steps=4,
        num_ppo_epochs=4,
        vf_coef=0.1,
        seed=42
    )


    trainer = PPOTrainer.from_config(
        config=config,
        model=model,
        tokenizer=tokenizer,
        ref_model=ref_model,
        train_dataset=train_dataset,
    )


    # PPO Loop
    for prompt, response in prompt_response_pairs:
        query_tensor = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).input_ids.to(model.device)
        response_tensor = tokenizer(response, return_tensors="pt", truncation=True, padding=True).input_ids.to(model.device)

        trainer.step([query_tensor], [response_tensor], score)

    print("PPO training complete.")




"""
prompts = []
prompts.append()

for prompt in prompts:
    
    response = ppo_trainer.generate(prompt)
    reward = compute_reward(response)  # 
    ppo_trainer.step([prompt], [response], [reward])
    
"""
    
    
    
    