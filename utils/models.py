
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from unsloth import FastLanguageModel
import gc

def load_quantized_model(model_path):
  """Carga el modelo indicado usando la librería transformers."""

  try:
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
      tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        dtype=torch.bfloat16,
        trust_remote_code=True
    )

    return model, tokenizer
  except Exception as e:
    print(f"Error cargando {model_path}: {e}")
    return None, None
  
def load_model_unsloth(model_path, max_seq_length=4096):
    """Carga el modelo indicado usando la librería unsloth. """
    try:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = model_path,
            max_seq_length = max_seq_length,
            load_in_4bit = True,
            dtype = None,
            device_map = "auto",
        )
        FastLanguageModel.for_inference(model)
        print(f"Modelo {model_path} cargado.")
        return model, tokenizer
    except Exception as e:
        print(f"Error cargando {model_path}: {e}")
        return None, None
    
def clear_memory():
    """Libera la VRAM de la GPU para poder cargar otro modelo."""
    gc.collect()
    torch.cuda.empty_cache()
    print("Memoria de la GPU liberada.")