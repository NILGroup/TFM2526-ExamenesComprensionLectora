uv run python -m matching_agents.run_matching matching_agents/data/matching.json \
  --backend gemini \
  --gemini-api-key "$GEMINI_API_KEY" \
  --trace \
  --output matching_agents/results/matching_dev.json


uv run python -m matching_agents.run_matching matching_agents/data/matching.json \
  --backend gemini \
  --gemini-api-key "$GEMINI_API_KEY" \
  --trace \
  --batch-size 3 \
  --batch-pause-seconds 2 \
  --output results/matching_full_gemini.json