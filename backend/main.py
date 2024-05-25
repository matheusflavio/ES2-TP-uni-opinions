from dataclasses import asdict
from beanie.odm.operators.find.comparison import In
from quart import Quart, request
from beanie import init_beanie
from quart_cors import cors, route_cors
from api_responses import (
    UserData,
    UserResponse,
    GenericResponse,
    ReviewData,
    ReviewResponse,
    SimpleData,
    SimpleResponse,
)
from db.Review import SortingMethod, Review
from db.Session import Session
from db.User import User
from db.Disciplina import Disciplina
from db.Turma import Turma
from db.Professor import Professor
from db.parse_login import create_mongodb_uri
from motor.motor_asyncio import AsyncIOMotorClient
from unidecode import unidecode
import dotenv
import os

app = Quart("review_professores")
app = cors(app, allow_origin="*")


@app.before_serving
async def init_database():
    """
    Inicializa o banco de dados antes de começar a receber requisições.
    """
    dotenv.load_dotenv()
    mongodb_server = os.getenv("MONGODB_SERVER")
    mongodb_port = os.getenv("MONGODB_PORT")
    mongodb_username = os.getenv("MONGODB_USERNAME")
    mongodb_password = os.getenv("MONGODB_PASSWORD")
    mongodb_database = os.getenv("MONGODB_DATABASE")

    uri = create_mongodb_uri(mongodb_server, mongodb_port, mongodb_username, mongodb_password)
    client = AsyncIOMotorClient(uri)
    await init_beanie(
        getattr(client, mongodb_database), document_models=[User, Session, Review, Disciplina, Turma, Professor]
    )


def bad_request():
    return asdict(GenericResponse(False, "Bad Request")), 400


@app.route("/verifica_sessao", methods=["POST"])
@route_cors(allow_origin="*")
async def verifica_sessao():
    """
    Verifica se a sessão de login é válida.
    Recebe um json com o campo "session".
    Retorna 403 se a sessão for inválida.
    """

    data = await request.json
    if data is None:
        return bad_request()

    session_val = data.get("session", "")
    session = await Session.find({"session_id": session_val}).first_or_none()
    if session is None:
        return asdict(GenericResponse(False, "Sessão inválida.")), 403
    else:
        if await session.is_expired():
            return asdict(GenericResponse(False, "Sessão expirada.")), 403
        return asdict(GenericResponse(True, "Sessão válida.", session.session_id)), 200


@app.route("/login", methods=["POST"])
@route_cors(allow_origin="*")
async def login():
    """
    Verifica as credenciais enviadas e faz login.
    Esse endpoint deve receber um application/json com os campos "username" e "password_hash"
    Retorna um LoginResponse com o objeto UserResponse caso as credenciais baterem.
    Retorna 401 caso contrário.
    Retorna 409 caso o usuário já estiver logado.
    Esse endpoint retorna o campo "session". Deve ser salvo como um cookie para requests futuros.
    """
    data = await request.json
    if not data:
        return bad_request()

    session_id = data.get("session", "")
    session = await find_session(session_id)
    if session and not await session.is_expired():
        user = await get_user_by_session(session)
        await session.renew()
        return handle_logged_in_user(user, session)

    username = data.get("username", "").strip()
    password_hash = data.get("password_hash", "")

    if not username or not password_hash:
        return bad_request()

    user = await find_user_by_username(username)
    if user and user.password_hash == password_hash:
        new_session = await create_new_session(user)
        return handle_successful_login(user, new_session)

    return handle_failed_login()


async def find_session(session_id):
    return await Session.find({"session_id": session_id}).first_or_none()


async def get_user_by_session(session):
    return await User.find({"user_id": session.linked_user_id}).first_or_none()


async def find_user_by_username(username):
    return await User.find({"safe_username": username.lower()}).first_or_none()


async def create_new_session(user):
    return await Session.create_session(user)


def handle_logged_in_user(user, session):
    user_data = UserData(user.user_id, user.username, user.upvoted_reviews, user.downvoted_reviews)
    return asdict(UserResponse(False, "Você já está logado!", user_data, session.session_id)), 409


def handle_successful_login(user, new_session):
    user_data = UserData(user.user_id, user.username, user.upvoted_reviews, user.downvoted_reviews)
    response = UserResponse(True, "Logado com sucesso.", user_data, new_session.session_id)
    return asdict(response), 200


def handle_failed_login():
    return asdict(UserResponse(False, "Credenciais incorretas.", None, "")), 401



@app.route("/register", methods=["POST"])
@route_cors(allow_origin="*")
async def register():
    """
    Registra o usuário no sistema.
    Caso já existir um usuário de mesmo nome, retorna 409.
    Caso os requisitos de senha e username não forem cumpridos, retorna 400.
    Esse endpoint retorna o campo "session". Deve ser salvo como um cookie para requests futuros.
    """
    data = await request.json
    if data is None:
        return bad_request()

    session_val = data.get("session", "")
    session = await Session.find({"session_id": session_val}).first_or_none()
    if session is not None:
        user = await User.find({"user_id": session.linked_user_id}).first_or_none()
        if not (await session.is_expired()):
            await session.renew()
            user = UserData(user.user_id, user.username, user.upvoted_reviews, user.downvoted_reviews)
            return asdict(UserResponse(False, "Você já está logado!", user, session.session_id)), 409

    username = data.get("username", "").strip()
    password_hash = data.get("password_hash", "")

    if not username or not password_hash:
        return bad_request()

    user = await User.find({"safe_username": username.lower()}).first_or_none()
    if user is not None:
        return asdict(UserResponse(False, "Já existe um usuário com esse nome.", None, "")), 409

    user_db = await User.create_user(username, password_hash)
    new_session = await Session.create_session(user_db)
    user = UserData(user_db.user_id, user_db.username, user_db.upvoted_reviews, user_db.downvoted_reviews)
    response = UserResponse(True, "Conta registrada com sucesso.", user, new_session.session_id)
    return asdict(response), 200


@app.route("/logout", methods=["POST"])
@route_cors(allow_origin="*")
async def logout():
    """
    Desconecta o usuário do sistema, deletando a sessão salva.
    Esse endpoint sempre retorna 200 dado que você passe um json com o parâmetro "session".
    Esse endpoint retorna o campo "session". Deve ser salvo como um cookie para requests futuros.
    """
    data = await request.json
    if data is None:
        return bad_request()

    session_val = data.get("session", "")
    session = await Session.find({"session_id": session_val}).first_or_none()
    if session is None:
        return asdict(GenericResponse(True, "Já desconectado.")), 200
    else:
        await session.delete_session()
        return asdict(GenericResponse(True, "Desconectado com sucesso.")), 200


@app.route("/fetch_disciplinas", methods=["GET"])
@route_cors(allow_origin="*")
async def fetch_disciplinas():
    """Retorna as disciplinas disponíveis no banco de dados"""
    disciplinas = await Disciplina.find({}).to_list()
    d = [SimpleData(d.id_disciplina, d.nome.strip()) for d in disciplinas]
    d.sort(key=lambda x: unidecode(x.nome).lower())
    return asdict(SimpleResponse(True, "Disciplinas obtidas com sucesso.", d)), 200


@app.route("/fetch_professores", methods=["POST"])
@route_cors(allow_origin="*")
async def fetch_professores():
    """
    Retorna todos os professores. Se "disciplina_id" for providenciado,
    retorna os professores que ofertaram tal disciplina.
    """
    data = await request.get_json(silent=True)
    if data is None:
        return bad_request()

    disciplina_id = data.get("disciplina_id", "")
    if not disciplina_id:
        professores = await Professor.find({}).to_list()
        d = [SimpleData(p.uid_professor, p.nome.strip()) for p in professores]
        d.sort(key=lambda x: unidecode(x.nome).lower())
        return asdict(SimpleResponse(True, "Professores obtidos com sucesso.", d)), 200
    else:
        turmas_da_disciplina = await Turma.find(Turma.id_disciplina == disciplina_id).to_list()
        professores_ids = [t.uid_professor_ministrante for t in turmas_da_disciplina]

        professores = await Professor.find(In(Professor.uid_professor, professores_ids)).to_list()
        p = [SimpleData(p.uid_professor, p.nome.strip()) for p in professores]
        p.sort(key=lambda x: unidecode(x.nome).lower())

        return asdict(SimpleResponse(True, "Professores obtidos com sucesso.", p)), 200


@app.route("/fetch_semestres", methods=["POST"])
@route_cors(allow_origin="*")
async def fetch_semestres():
    """
    Retorna todos os semestres.
    Se "professor_id" e "disciplina_id" forem providenciados,
    retorna os semestres que o professor deu a disciplina.
    """
    data = await request.get_json(silent=True)
    if data is None:
        return bad_request()

    disciplina_id = data.get("disciplina_id", "")
    professor_id = data.get("professor_id", "")
    if not disciplina_id or not professor_id:
        turmas = await Turma.distinct("semestre")
        turmas.sort(reverse=True)
        s = [SimpleData(None, s) for s in turmas]
        return asdict(SimpleResponse(True, "Semestres obtidos com sucesso.", s)), 200

    turmas_da_disciplina = (
        await Turma.find(Turma.id_disciplina == disciplina_id, Turma.uid_professor_ministrante == professor_id)
        .sort(("-semestre"))
        .to_list()
    )
    semestres = [t.semestre for t in turmas_da_disciplina]
    r = [SimpleData(None, s) for s in semestres]

    return asdict(SimpleResponse(True, "Semestres obtidos com sucesso.", r)), 200


@app.route("/create_review", methods=["POST"])
@route_cors(allow_origin="*")
async def create_review():
    """
    Cria uma review no site.
    O json de requisição deve ser algo do tipo:
    {
        "semester": "2021/2",
        "teacher_id": "120526b0-9a0a-498c-acae-8d25a98d03e1",
        "disciplina_id": "f0fc331b-1bb7-4978-91c6-ffff45141658",
        "is_anonymous": false,
        "content": "muito bom o professor, mas no maximo 500 caracteres",
        "session": "valor_aqui"
    }
    Retorna 403 se não estiver logado.
    Retorna 404 se a disciplina ou o professor não forem encontrados.
    Retorna 413 se a mensagem for grande demais.
    """
    data = await request.json
    if data is None:
        return bad_request()

    session = await get_session(data.get("session"))
    if not session or await session.is_expired():
        return asdict(GenericResponse(False, "Você não está logado ou sua sessão expirou.")), 403

    user = await get_user(session)
    if not user:
        await session.delete_session()
        return asdict(GenericResponse(False, "Conta inexistente.")), 403

    semester = data.get("semester")
    teacher_id = data.get("teacher_id")
    disciplina_id = data.get("disciplina_id")
    content = data.get("content")
    is_anonymous = data.get("is_anonymous")

    if not semester or not teacher_id or not disciplina_id or not content or is_anonymous is None:
        return bad_request()

    if len(content) > 500:
        return asdict(GenericResponse(False, "Mensagem grande demais.")), 413

    teacher = await get_teacher(teacher_id)
    if not teacher:
        return asdict(GenericResponse(False, "Professor inexistente.")), 404

    disciplina = await get_disciplina(disciplina_id)
    if not disciplina:
        return asdict(GenericResponse(False, "Disciplina inexistente.")), 404

    turma = await get_turma(disciplina.id_disciplina, teacher.uid_professor, semester)
    if not turma:
        return asdict(GenericResponse(False, "Esse professor não ministrou essa matéria nesse semestre.")), 404

    review_obj = await create_new_review(user, is_anonymous, teacher.uid_professor, disciplina.id_disciplina, semester, content)

    await user.save()

    review_data = await prepare_review_data(review_obj, semester, teacher.nome, disciplina.nome)
    return asdict(ReviewResponse(True, "Review criado com sucesso!", [review_data])), 200


async def get_session(session_id):
    return await Session.find({"session_id": session_id}).first_or_none()


async def get_user(session):
    return await User.find(User.user_id == session.linked_user_id).first_or_none()


async def get_teacher(teacher_id):
    return await Professor.find(Professor.uid_professor == teacher_id).first_or_none()


async def get_disciplina(disciplina_id):
    return await Disciplina.find(Disciplina.id_disciplina == disciplina_id).first_or_none()


async def get_turma(disciplina_id, professor_id, semester):
    return await Turma.find(
        Turma.id_disciplina == disciplina_id,
        Turma.uid_professor_ministrante == professor_id,
        Turma.semestre == semester,
    ).first_or_none()


async def create_new_review(user, is_anonymous, teacher_id, disciplina_id, semester, content):
    review_obj = await Review.create_review(
        user.username, user.user_id, is_anonymous, teacher_id, disciplina_id, semester, content
    )
    user.upvoted_reviews.append(review_obj.id_review)
    return review_obj


async def prepare_review_data(review_obj, semester, professor_name, disciplina_name):
    return ReviewData(
        review_id=review_obj.id_review,
        autor="Anônimo" if review_obj.is_anonymous else review_obj.author,
        content=review_obj.content,
        time=review_obj.time,
        votes=review_obj.n_votes,
        semester=semester,
        professor=professor_name,
        disciplina=disciplina_name,
    )



@app.route("/fetch_review", methods=["POST"])
@route_cors(allow_origin="*")
async def fetch_review():
    data = await request.json
    if data is None:
        return bad_request()

    sorting_method = data.get("sorting")
    if sorting_method not in [method.value for method in SortingMethod]:
        return bad_request()

    try:
        range_start = int(data.get("range_start", 0))
        range_end = int(data.get("range_end", 15))
    except ValueError:
        return bad_request()

    mongodb_query = {}
    semester = data.get("semester")
    if semester:
        mongodb_query["semester"] = semester

    teacher_id = data.get("teacher_id")
    if teacher_id:
        mongodb_query["teacher_id"] = teacher_id

    disciplina_id = data.get("disciplina_id")
    if disciplina_id:
        mongodb_query["disciplina_id"] = disciplina_id

    sort_criteria = get_sort_criteria(sorting_method)

    reviews = await fetch_reviews_from_database(mongodb_query, sort_criteria, range_start, range_end)

    # Aguardando a formatação dos dados para garantir que seja concluída antes de prosseguir
    response_data = await format_reviews_data(reviews)

    return asdict(ReviewResponse(True, "Dados obtidos com sucesso!", response_data)), 200


def get_sort_criteria(sorting_method):
    if sorting_method == SortingMethod.NEWEST_FIRST:
        return ("-time", "-n_votes")
    elif sorting_method == SortingMethod.OLDEST_FIRST:
        return ("+time", "-n_votes")
    elif sorting_method == SortingMethod.MOST_UPVOTED:
        return ("-n_votes", "-time")
    elif sorting_method == SortingMethod.LEAST_UPVOTED:
        return ("+n_votes", "-time")

async def fetch_reviews_from_database(query, sort_criteria, range_start, range_end):
    return await Review.find(query).skip(range_start).limit(range_end - range_start).sort(*sort_criteria).to_list()

async def format_reviews_data(reviews):
    response_data = []
    for result in reviews:
        disciplina = await Disciplina.find(Disciplina.id_disciplina == result.disciplina_id).first_or_none()
        professor = await Professor.find(Professor.uid_professor == result.teacher_id).first_or_none()
        if disciplina and professor:
            response_data.append(format_review(result, disciplina.nome, professor.nome))
    return response_data

def format_review(review, disciplina_nome, professor_nome):
    return ReviewData(
        review_id=review.id_review,
        autor="Anônimo" if review.is_anonymous else review.author,
        content=review.content,
        time=review.time,
        votes=review.n_votes,
        semester=review.semester,
        professor=professor_nome,
        disciplina=disciplina_nome,
    )



@app.route("/upvote_review", methods=["POST"])
@route_cors(allow_origin="*")
async def upvote_review():
    """
    Dá upvote em um review.
    O json de requisição deve ter o campo "review_id" indicando o id do review a ser upvotado.
    O json de requisição deve ter o campo "session" indicando o token de sessão.
    Retorna 403 caso o usuário não estiver logado.
    Retorna 404 caso o review não existir.
    """
    data = await request.json
    if data is None:
        return bad_request()

    session_val = data.get("session", "")
    session = await Session.find({"session_id": session_val}).first_or_none()
    if session is None:
        return asdict(GenericResponse(False, "Você não está logado!")), 403
    else:
        if await session.is_expired():
            return asdict(GenericResponse(False, "Por favor, faça login novamente.")), 403

    user = await User.find(User.user_id == session.linked_user_id).first_or_none()
    if user is None:
        await session.delete_session()
        return asdict(GenericResponse(False, "Conta inexistente.")), 403

    review_id = data.get("review_id", "")
    if not review_id:
        return bad_request()

    review = await Review.find(Review.id_review == review_id).first_or_none()
    if review is None:
        return asdict(GenericResponse(False, "Review não encontrada.")), 404

    if review.id_review in user.upvoted_reviews:
        user.upvoted_reviews.remove(review.id_review)
        review.n_votes -= 1
        await user.save()
        await review.save()
        return asdict(GenericResponse(True, "Upvote desfeito com sucesso.")), 200
    elif review.id_review in user.downvoted_reviews:
        user.downvoted_reviews.remove(review.id_review)
        user.upvoted_reviews.append(review.id_review)
        review.n_votes += 2
        await user.save()
        await review.save()
    else:
        user.upvoted_reviews.append(review.id_review)
        review.n_votes += 1
        await user.save()
        await review.save()

    return asdict(GenericResponse(True, "Upvote computado com sucesso.")), 200


@app.route("/downvote_review", methods=["POST"])
@route_cors(allow_origin="*")
async def downvote_review():
    """
    Dá downvote em um review.
    O json de requisição deve ter o campo "review_id" indicando o id do review a ser downvotado.
    O json de requisição deve ter o campo "session" indicando o token de sessão.
    Retorna 403 caso o usuário não estiver logado.
    Retorna 404 caso o review não existir.
    Retorna 409 se o review já tiver sido downvotado pelo usuário.
    """
    data = await request.json
    if data is None:
        return bad_request()

    session_val = data.get("session", "")
    session = await Session.find({"session_id": session_val}).first_or_none()
    if session is None:
        return asdict(GenericResponse(False, "Você não está logado!")), 403
    else:
        if await session.is_expired():
            return asdict(GenericResponse(False, "Por favor, faça login novamente.")), 403

    user = await User.find(User.user_id == session.linked_user_id).first_or_none()
    if user is None:
        await session.delete_session()
        return asdict(GenericResponse(False, "Conta inexistente.")), 403

    review_id = data.get("review_id", "")
    if not review_id:
        return bad_request()

    review = await Review.find(Review.id_review == review_id).first_or_none()
    if review is None:
        return asdict(GenericResponse(False, "Review não encontrada.")), 404

    if review.id_review in user.downvoted_reviews:
        user.downvoted_reviews.remove(review.id_review)
        review.n_votes += 1
        await user.save()
        await review.save()
        return asdict(GenericResponse(True, "Downvote desfeito com sucesso.")), 200
    elif review.id_review in user.upvoted_reviews:
        user.upvoted_reviews.remove(review.id_review)
        user.downvoted_reviews.append(review.id_review)
        review.n_votes -= 2
        await user.save()
        await review.save()
    else:
        user.downvoted_reviews.append(review.id_review)
        review.n_votes -= 1
        await user.save()
        await review.save()

    return asdict(GenericResponse(True, "Downvote computado com sucesso.")), 200


if __name__ == "__main__":
    app.run()