# ComplaintScope Makefile
# Cross-platform friendly automation targets

PYTHON := .venv\Scripts\python.exe
PYTEST := .venv\Scripts\pytest.exe
STREAMLIT := .venv\Scripts\streamlit.exe

.PHONY: setup data fast all app report slides test clean

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm
	$(PYTHON) -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

data:
	$(PYTHON) -m src.data

fast:
	$(PYTHON) -c "import yaml; cfg = yaml.safe_load(open('config.yaml')); cfg['mode']='fast'; yaml.safe_dump(cfg, open('config.yaml','w'))"
	$(PYTHON) -m src.data
	$(PYTHON) -m src.preprocess
	$(PYTHON) -m src.features
	$(PYTHON) -m src.classify
	$(PYTHON) -m src.relief
	$(PYTHON) -m src.topics
	$(PYTHON) -m src.emerging
	$(PYTHON) -m src.network
	$(PYTHON) -m src.risk_index

all:
	$(PYTHON) -c "import yaml; cfg = yaml.safe_load(open('config.yaml')); cfg['mode']='full'; yaml.safe_dump(cfg, open('config.yaml','w'))"
	$(PYTHON) -m src.data
	$(PYTHON) -m src.preprocess
	$(PYTHON) -m src.features
	$(PYTHON) -m src.classify
	$(PYTHON) -m src.relief
	$(PYTHON) -m src.topics
	$(PYTHON) -m src.emerging
	$(PYTHON) -m src.network
	$(PYTHON) -m src.risk_index
	$(PYTHON) -m src.report_builder
	$(PYTHON) -m src.slides_builder

app:
	$(STREAMLIT) run app/streamlit_app.py

report:
	$(PYTHON) -m src.report_builder

slides:
	$(PYTHON) -m src.slides_builder

test:
	$(PYTEST) tests/ -v

clean:
	rm -rf data/interim/*
	rm -rf app/artifacts/*
	rm -rf results/figures/*
	rm -rf results/tables/*
	rm -rf results/metrics/*
