import torch

# -------------------------------------------------------------------
# UNSLOTH LOADER
# -------------------------------------------------------------------
def load_model_unsloth(model_name, max_seq_length=4096, dtype=None, load_in_4bit=True):
    """
    Carga un modelo y su tokenizador usando Unsloth y lo prepara para inferencia.
    """
    # Import inside the function (or at the top of the file)
    from unsloth import FastLanguageModel
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    # Prepares the model for faster inference (2x faster)
    FastLanguageModel.for_inference(model)

    return model, tokenizer


# -------------------------------------------------------------------
# HUGGING FACE TRANSFORMERS LOADER
# -------------------------------------------------------------------
def load_model_transformers(model_name, max_seq_length=4096, dtype=None, load_in_4bit=True):
    """
    Carga un modelo y su tokenizador usando la librería estándar de Transformers.
    Soporta cuantización a 4-bit usando bitsandbytes.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    
    # 1. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 2. Automatically detect best dtype if none is provided
    if dtype is None:
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

    # 3. Setup 4-bit Quantization Config (Equivalent to Unsloth's native 4-bit)
    quantization_config = None
    if load_in_4bit:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,     # Recommended for memory savings
            bnb_4bit_quant_type="nf4"           # Recommended for LLMs
        )

    # 4. Load the Model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        quantization_config=quantization_config,
        device_map="auto",              # Automatically maps layers to GPU/CPU
        low_cpu_mem_usage=True,         # Keeps RAM usage low during loading
        trust_remote_code=True          # Required for some custom models
    )

    return model, tokenizer