# TP_Engenharia_De_Software_2

# Membros
Matheus Flávio Gonçalves Silva

# Explicação sobre o sistema
Para esse sistema web é idealizado um fórum de avaliação a respeito de professores da UFMG com dados referentes ao período de 2020/1 a 2023/1, com classificação pro semestre lecionado validação se o professor deu aula da matéria no semestre, podendo ser feitas avaliações de forma anônima ou sem anonimato de acordo com o usuário.

# Tecnologias
- Quart
- React
- MongoDB

# Instruções de instalação e uso

## Instalação
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

### Erro: Apagar e criar o Bando de Dados novamente
Em caso de erro, existe uma chance de o mongo já ter um Banco de Dados com nome "professores".
Caso não seja um banco importante, sugiro apagar e criar novamente o Banco de Dados para usar o sistema.

```bash
cd backend
mongo
show dbs # para conferir se existe um Banco de Dados chamado professores
use professores
db.dropDatabase()
exit
python3 db/load_classes_from_csv.py db/classes.csv
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