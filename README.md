# TP_Engenharia_De_Software_2

# Membros
Matheus Flávio Gonçalves Silva

# Explicação sobre o sistema
Para esse sistema web é idealizado um fórum de avaliação a respeito de professores da UFMG com dados referentes ao período de 2020/1 a 2023/1, com classificação pro semestre lecionado validação se o professor deu aula da matéria no semestre, podendo ser feitas avaliações de forma anônima ou sem anonimato de acordo com o usuário.

# Tecnologias
## Backend
### Quart
Foi escolhido o Quart como backend pela facilidade da manipulação da linguagem Python e pela similaridade com o framework Flask utilizado para desenvolvimento Web. De certo modo, pode-se dizer que o Quart é a reimplementação do Flask com a possibilidade de execução de funções assíncronas, tal qual explicita a página oficiail do framework:
<a href="https://pgjones.gitlab.io/quart/#:~:text=Quart%20is%20an%20asyncio%20reimplementation%20of%20the%20popular%20Flask%20microframework%20API.%20This%20means%20that%20if%20you%20understand%20Flask%20you%20understand%20Quart.%20See%20Flask%20evolution%20to%20learn%20more%20about%20how%20Quart%20builds%20on%20Flask.">Documentação Oficial com a passagem selecionada</a>
### React
Foi escolhido o React como ferramenta para desenvolvimento do frontend pela maior intimidade com esse framework.
### MongoDB
Para o banco de dados foi escolhido o MongoDB pela possibilidade de utilização do MongoDB Compass facilitar a correção de pequenos problemas, a visualização dos dados e correção do banco. Foram cogitados também os bandos MySQL e SQLite, mas deixados de lado em virtude da experiência de maior facilidade de lidar com o MongoDB. 

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

Execute a sequência abaixo a partir da pasta raiz do projeto:
```bash
cd backend
mongo
show dbs # para conferir se existe um Banco de Dados chamado professores
use professores
db.dropDatabase()
exit
python3 db/load_classes_from_csv.py db/classes.csv
cd..
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

# Formatação do código (opicional)
```bash
## backend
cd backend
find . -name '*.py' -print0 | xargs -0 python3 -m black --line-length=120
cd ..
```