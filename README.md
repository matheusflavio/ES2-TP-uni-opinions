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
O banco de dados utilizado é o MongoDB. Basta tê-lo instalado e operacional para rodar o sistema corretamente.

## Download do repositório
```bash
git clone https://github.com/matheusflavio/ES2-TP-uni-opinions
cd ES2-TP-uni-opinions
```

## Configuração do ambiente com VENV (Opicional)
```bash
pip3 install virtualenv
python3 -m venv pyvirtual
source pyvirtual/bin/activate
```

## Configuração do backend + Banco de Dados
```bash
cd backend
python3 -m pip install -r requirements.txt
cp .env_example .env
python3 db/load_classes_from_csv.py db/classes.csv
cd ..
```

### Erro
Em caso de erro, existe uma chance de o mongo já ter um Banco de Dados com nome "Professores".
Caso não seja um banco importante, sugiro que faça o drop dele para utilizar o sistema sem problemas.

```bash
mongo
show dbs # para conferir se existe um Banco de Dados chamado Professores
use Professor
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