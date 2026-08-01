# Run these first

conda create -n crude-advisor python=3.11

conda activate crude-advisor

conda install -c conda-forge scip

pip install -r requirements.txt

python orchestrator.py

## download ollama
irm https://ollama.com/install.ps1 | iex

check:


ollama --version

then run:

ollama pull qwen3:8b