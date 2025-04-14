# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""An common abstraction for a cached LLM inference setup. Currently supports OpenAI's gpt-4-turbo."""

import os
#from openai import OpenAI
from pathlib import Path
import json

CACHE_DIR = Path("./cache_dir")
CACHE_PATH = CACHE_DIR / "cache.json"


class Cache:
    """A simple cache implementation to store the results of the LLM inference."""

    def __init__(self) -> None:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH) as f:
                self.cache_dict = json.load(f)
        else:
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.cache_dict = {}

    @staticmethod
    def process_payload(payload):
        if isinstance(payload, (list, dict)):
            return json.dumps(payload)
        return payload

    def get_from_cache(self, payload):
        payload_cache = self.process_payload(payload)
        if payload_cache in self.cache_dict:
            return self.cache_dict[payload_cache]
        return None

    def add_to_cache(self, payload, output):
        payload_cache = self.process_payload(payload)
        self.cache_dict[payload_cache] = output

    def save_cache(self):
        with open(CACHE_PATH, "w") as f:
            json.dump(self.cache_dict, f, indent=4)


class GPT4Turbo:
    """Abstraction for OpenAI's GPT-4 Turbo model."""

    def __init__(self):
        self.cache = Cache()

    def inference(self, payload: list[dict[str, str]]) -> list[str]:
        if self.cache is not None:
            cache_result = self.cache.get_from_cache(payload)
            if cache_result is not None:
                return cache_result

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        try:
            response = client.chat.completions.create(
                messages=payload,  # type: ignore
                model="gpt-4o-mini",
                max_tokens=1024,
                temperature=0.5,
                top_p=0.95,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                n=1,
                timeout=60,
                stop=[],
            )
        except Exception as e:
            print(f"Exception: {repr(e)}")
            raise e

        return [c.message.content for c in response.choices]  # type: ignore

    def run(self, payload: list[dict[str, str]]) -> list[str]:
        response = self.inference(payload)
        if self.cache is not None:
            self.cache.add_to_cache(payload, response)
            self.cache.save_cache()
        return response

class T5Turbo:
    """Abstraction for Google's T5 model."""

    def __init__(self, model_name: str = "t5-base"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.cache = Cache()

    def inference(self, input_text: str, max_length: int = 512) -> str:
        if self.cache is not None:
            cache_result = self.cache.get_from_cache(input_text)
            if cache_result is not None:
                return cache_result

        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_length=max_length)
        result = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        return result

    def run(self, input_text: str) -> str:
        response = self.inference(input_text)
        if self.cache is not None:
            self.cache.add_to_cache(input_text, response)
            self.cache.save_cache()
        return response
