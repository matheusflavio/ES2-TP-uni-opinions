# TP_Engenharia_De_Software_2
## Objetivo
Para esse projeto é idealizado um fórum de avaliação e discussão sobre professores da UFMG com classificação pro semestre lecionado.

# Membros
Matheus Flávio Gonçalves Silva

# Tecnologias
- Quart
- React
- MongoDB

# Instalação
## Download do repositório
```bash
git clone https://github.com/matheusflavio/ES2-TP-uni-opinions
```

## Configuração do ambiente
```bash
cd ES2-TP-uni-opinions
sudo apt update && sudo apt upgrade
pip3 install venv
python3 -m venv pyvirtual
source pyvirtual
```

## Configuração do backend + Banco de Dados
```bash
cd backend
python3 -m pip install -r requirements.txt
cp .env_example .env
python3 db/load_classes_from_csv.py db/classes.csv
cd ..
```

## Configuração do frontend
```bash
cd frontend
npm i
cd review-profs
npm i
cd ..
cd ..

```

## Rodando os servidores
```bash
./start.sh
```

# Formatação do código
```bash
## backend
cd backend
find . -name '*.py' -print0 | xargs -0 python3 -m black --line-length=120
cd ..
```