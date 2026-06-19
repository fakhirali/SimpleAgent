#!/usr/bin/env bash
export CC=/usr/bin/gcc-12
export CXX=/usr/bin/g++-12
export CUDAHOSTCXX=/usr/bin/g++-12
export HF_HUB_DISABLE_PROGRESS_BARS=0
export VLLM_LOGGING_LEVEL=DEBUG
source /home/fakhir/Code/SimpleAgent/.venv/bin/activate
exec vllm serve RedHatAI/Qwen3.5-4B-FP8-dynamic \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.85 \
  --max-num-seqs 16 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --language-model-only
