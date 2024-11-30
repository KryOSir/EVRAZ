import string
import requests
import os

REVIEWS_TREE = [
    {"code": r"2020.2-Anunbis-develop\2020.2-Anunbis-develop\app\__init__.py",
     "review": "TODO: необходимо привести структуру проекта к стандартам"},
    {"code": r"2020.2-Anunbis-develop\2020.2-Anunbis-develop\app\services\auth_services.py",
     "review": "TODO: HTTP код ответа нужно расместить в контроллерах"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\routes.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/api/app.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\users\api.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/api/controllers/user.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\users\mixins.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/api/controllers/base.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\users\models.py",
     "review": "TODO Перенести этот модуль в components/app/application/entities.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\users\tests.py",
     "review": "TODO Перенести этот модуль в components/app/tests/integration/adapters/api/controllers/test_user.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\utils\auth.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/api/auth.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\utils\errors.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/api/errors.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\utils\misc.py",
     "review": "TODO Перенести этот модуль в components/app/application/utils.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\app\utils\testing.py",
     "review": "TODO Перенести этот модуль в components/app/tests/integration/adapters/api/controllers/conftest.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\migrations\env.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/db/alembic/app.py"},
    {"code": r"Flask-PostgreSQL-API-Seed-master\Flask-PostgreSQL-API-Seed-master\migrations\versions\351c26992f23_.py",
     "review": "TODO Перенести этот модуль в components/app/adapters/db/migrations/app.py"},
    {"code": r"FlaskApiEcommerce-master\FlaskApiEcommerce-master\FlaskApiEcommerce-master\ecommerce_api\factory.py",
     "review": "TODO: вынести в app.py"},
    {"code": r"RESTfulAPI-master 2\RESTfulAPI-master\RESTfulApi\app.py",
     "review": "TODO: перенести в слой adapter"},
    {"code": r"RESTfulAPI-master 2\RESTfulAPI-master\run.py",
     "review": "TODO: перенести в композит"},
    {"code": r"backend-master\backend-master\freenit\api\__init__.py",
     "review": "TODO: Вынести в слой adapters/api"},
    {"code": r"gramps-web-api-master\gramps-web-api-master\gramps_webapi\api\file.py",
     "review": "TODO: перенести в слой адаптеров"},
    {"code": r"luncher-api-master\luncher-api-master\conftest.py",
     "review": "TODO: по стандарту удаляем"},
    {"code": r"final-year-project-backend-api-master\final-year-project-backend-api-master\api\__init__.py",
     "review": "TODO: вынести в модуль app"}
]

REVIEWS_CODE = [
    {"code": "user, status_code = auth_services.auth_user(user)",
     "review": "TODO: auth_services следует передавать через DI."},
    {"code": "message['contact_us'] = current_app.config['ANUNBIS_FRONTEND_URI']",
     "review": "TODO: настройка должна передаваться через DI."},
    {"code": "from fastapi import FastAPI",
     "review": "TODO: рекомендуется использовать Falcon вместо FastAPI."},
    {"code": "class BaseConfig:    ...",
     "review": "TODO: используйте pydantic, перенесите настройки в .env, разделите настройки по модулям."},
    {"code": "class DevConfig(BaseConfig):    ...",
     "review": "TODO: используйте pydantic, перенесите настройки в .env, разделите настройки по модулям."},
    {"code": "return {'message': 'User's email not actived. Please, active your e-mail!'}, 203",
     "review": "TODO: определите HTTP коды ответов в контроллерах."},
    {"code": "rest_api.add_resource(...",
     "review": "TODO: преобразуйте в фабричный метод."},
    {"code": "db.session.commit()",
     "review": "TODO: управляйте транзакциями централизованно через декораторы или базовые классы."},
    {"code": "req_parser = reqparse.RequestParser()   ...",
     "review": "TODO: используйте базовый класс, унаследованный от restful.Resource."},
    {"code": "id = db.Column(...",
     "review": "TODO: перенесите маппинг SQLAlchemy в отдельный файл."},
    {"code": "class Address(db.Model):",
     "review": "TODO: вынесите все модели в entities.py."},
    {"code": "    def get_summary(...",
     "review": "TODO: сериализацию вынесите в контроллеры."},
    {"code": "@blueprint.route('/users/addresses', methods=['GET'])\n@jwt_required\n...",
     "review": "TODO: оберните функционал в класс и вынесите в контроллеры."},
    {
        "code": "addresses = Address.query.filter_by(user_id=user_id).order_by(desc(Address.created_at)) \\ .paginate(page=page, per_page=page_size)",
        "review": "TODO: работу с БД вынести в адаптеры",
    },
    {"code": "first_name = request.json.get('first_name')\nlast_name = request.json.get('last_name')\nzip_code = request.json.get('zip_code')\nphone_number = request.json.get('phone_number')\ncity = request.json.get('city')\ncountry = request.json.get('country')\nstreet_address = request.json.get('address')",
        "review": "TODO: для всех эндпоинтов внедрить модели валидации Pydantic",
    },
    {
        "code": "db.session.add(address)\ndb.session.commit()",
        "review": "TODO: работу с БД вынести в адаптеры",
    },
    {
        "code": "app.register_blueprint(blueprint, url_prefix='/api')\n@app.shell_context_processor\ndef make_shell_context():\n    return dict(app=app, db=db, User=User, address=Address, order=Order, product=Product,\n                tag=Tag, category=Category, comment=Comment, file_upload=FileUpload, tag_image=TagImage,\n                category_image=CategoryImage, product_image=ProductImage)",
        "review": "TODO: создать экземпляры классов и внедрить как зависимости",
    },
    {
        "code": "products_categories = \\\n    db.Table('products_categories',\n             db.Column('category_id', db.Integer, db.ForeignKey('categories.id')),\n             db.Column('product_id', db.Integer, db.ForeignKey('products.id')))",
        "review": "TODO: все таблицы вынести в tables.py",
    },
    {
        "code": "basedir = os.path.abspath(os.path.dirname(__file__))\napp = Flask(__name__, root_path=os.getcwd(), static_url_path='/static')\n\napp.config.from_object(Config)\ndb = SQLAlchemy(app)\nmigrate = Migrate(app, db)\ncache = Cache()\n\ncors = CORS(app)\nbcrypt = Bcrypt()\njwt = JWTManager(app)",
        "review": "TODO: реализовать фабрику Flask, принимающую сервисы и настройки",
    },
    {
        "code": "@app.route('/routes')\ndef site_map():\n    links = []\n    for rule in app.url_map._rules:\n        links.append({'url': rule.rule, 'view': rule.endpoint})\n    return jsonify(links), 200",
        "review": "TODO: вынести в контроллеры",
    },
    {
        "code": "cart_items = request.json.get('cart_items')\nproduct_ids = [ci['id'] for ci in cart_items]\nproducts = db.session.query(Product).filter(Product.id.in_(product_ids)).all()",
        "review": "TODO: логику перенести в слой сервисов",
    },
    {
        "code": "class Request:   def __getattr__(self, item):       return getattr(request, item)\nclass APIView(MethodView):   def __init__(self, request) -> None:       self.request = request or Request()",
        "review": "TODO: отсутсвуют типы данных, в возвращаемых функциях указаны частично"
    },
    {
        "code": "class ContentType:   MULTIPART_FORM_DATA = 'multipart/form-data'   APPLICATION_JSON = 'application/json'",
        "review": "TODO: Не похоже на utils"
    },
    {
        "code": "class HTTPStatus:   HTTP_100_CONTINUE = 100   HTTP_101_SWITCHING_PROTOCOLS = 101   HTTP_200_OK = 200   HTTP_201_CREATED = 201   HTTP_202_ACCEPTED = 202   HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203   HTTP_204_NO_CONTENT = 204   HTTP_205_RESET_CONTENT = 205   HTTP_206_PARTIAL_CONTENT = 206   HTTP_207_MULTI_STATUS = 207   HTTP_300_MULTIPLE_CHOICES = 300   HTTP_301_MOVED_PERMANENTLY = 301   HTTP_302_FOUND = 302   HTTP_303_SEE_OTHER = 303   HTTP_304_NOT_MODIFIED = 304   HTTP_305_USE_PROXY = 305   HTTP_306_RESERVED = 306   HTTP_307_TEMPORARY_REDIRECT = 307   HTTP_400_BAD_REQUEST = 400   HTTP_401_UNAUTHORIZED = 401   HTTP_402_PAYMENT_REQUIRED = 402   HTTP_403_FORBIDDEN = 403   HTTP_404_NOT_FOUND = 404   HTTP_405_METHOD_NOT_ALLOWED = 405   HTTP_406_NOT_ACCEPTABLE = 406   HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407   HTTP_408_REQUEST_TIMEOUT = 408   HTTP_409_CONFLICT = 409   HTTP_410_GONE = 410   HTTP_411_LENGTH_REQUIRED = 411   HTTP_412_PRECONDITION_FAILED = 412   HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413   HTTP_414_REQUEST_URI_TOO_LONG = 414   HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415   HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416   HTTP_417_EXPECTATION_FAILED = 417   HTTP_422_UNPROCESSABLE_ENTITY = 422   HTTP_423_LOCKED = 423   HTTP_424_FAILED_DEPENDENCY = 42   HTTP_428_PRECONDITION_REQUIRED = 428   HTTP_429_TOO_MANY_REQUESTS = 429   HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431   HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451   HTTP_500_INTERNAL_SERVER_ERROR = 500   HTTP_501_NOT_IMPLEMENTED = 501   HTTP_502_BAD_GATEWAY = 502   HTTP_503_SERVICE_UNAVAILABLE = 503   HTTP_504_GATEWAY_TIMEOUT = 504   HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505   HTTP_507_INSUFFICIENT_STORAGE = 507   HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511",
        "review": "TODO: Не похоже на utils"
    },
    {
        "code": "__version__ = '2.2.0'\nDEBUG = os.environ.get('DEBUG', False)\nMODEL_NAME = os.environ.get('MODEL_NAME', 'model.joblib')\nENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')\nMODEL_TYPE = os.environ.get('MODEL_TYPE', 'SKLEARN_MODEL')\nSERVICE_START_TIMESTAMP = time()\napplication = flask.Flask(__name__)\napplication.logger.setLevel(logging.DEBUG if DEBUG else logging.ERROR)\napplication.json_encoder = ExtendedEncoder\nmodel = ModelFactory.create_model(MODEL_NAME, MODEL_TYPE)\napplication.logger.info('ENVIRONMENT: {}'.format(ENVIRONMENT))\napplication.logger.info('Using template version: {}'.format(__version__))\napplication.logger.info('Loading model...')\nmodel.load()",
        "review": "TODO: Монолит, все в одном месте, логика, точка входа, роутинг"
    },
    {
        "code": "app = create_app(os.environ.get('FLASK_ENV'))",
        "review": "TODO: вынести в настройки с использованием BaseSettings"
    },
    {
        "code": "@app.cli.command()\ndef run():   app.run(host='0.0.0.0')\n@app.cli.command()\ndef test():   tests = unittest.TestLoader().discover('test', pattern='test*.py')   result = unittest.TextTestRunner(verbosity=2).run(tests)   return result.wasSuccessful()",
        "review": "TODO: вынести в адаптер cli"
    },
    {
        "code": "@app.after_request\ndef log_info(response):   date = arrow.now('Africa/Lagos')   if os.environ.get('FLASK_ENV') is 'prod':       ip = request.headers.get(app.config['REAL_IP'])   else:       ip = request.remote_addr   log_details = {       'date': date.format(),       'ip': ip,       'browser': request.user_agent.browser,       'device': request.user_agent.platform,       'status_code': response.status_code,       'path': request.path,       'method': request.method,   }   response.headers.add('Access-Control-Allow-Origin', '*')   response.headers.add('Access-Control-Allow-Headers', 'Content-Type, x-auth-token')   stream_logger.debug(log_details)   if not app.debug:       request_logger.info(log_details)   return response",
        "review": "TODO: вынести в адаптер logger"
    },
    {
        "code": "db = SQLAlchemy()\nmail = Mail()\nauthorizations = {   'apiKey': {       'type': 'apiKey',       'in': 'header',       'name': 'x-auth-token'   }\n}",
        "review": "TODO: экземпляры подключений, севрисов итд прокидывать через DI"
    },
    {
        "code": "def create_app(config_name):   app = Flask(__name__)   app.wsgi_app = ProxyFix(app.wsgi_app)   app.config.from_object(config_by_env[config_name])   db.init_app(app)   mail.init_app(app)   api.init_app(app)",
        "review": "TODO: фабрика должна принимать сервисы и регистрировать контроллеры"
    },
    {
        "code": "admin_api = Namespace('admins', description='Endpoints to manage admin operations')",
        "review": "TODO: регистрация эндпоинтов необходимо вынести в фабрику создания app"
    },
    {
        "code": "admin_reg = admin_api.model('Admin Registration', {   'name': fields.String(required=True, description='Admin\'s name'),   'email': fields.String(required=True, description='Admin\'s email'),   'password': fields.String(required=True, description='Admin\'s password')\n})",
        "review": "TODO: модели стоит вынести в отдельный пакет"
    },
    {
        "code": "@admin_api.route('/signup')\nclass Signup(Resource):   @admin_api.doc('Register a new Admin')   @admin_api.response(201, 'New Admin successfully registered')   @admin_api.expect(admin_reg)   def post(self):       data = request.json       payload = admin_api.payload or data       schema = NewAdminSchema()",
        "review": "TODO: регистрация эндпоинтов необходимо вынести в фабрику создания app"
    },
    {
        "code": "response, code = AdminsService.create(data=new_payload)       return response, code",
        "review": "TODO: сервисы необходимо прокидывать как зависимость"
    },
    {
        "code": "@admin_api.route('/exam/oar/<string:session>/<string:semester>/<string:course>/<string:department>')",
        "review": "TODO: вынести роут в константы"
    },
    {
        "code": "class Admin(db.Model):   __tablename__ = 'admins'    id = db.Column(db.Integer, primary_key=True, autoincrement=True)   name = db.Column(db.String(128))   email = db.Column(db.String(128))   password_hash = db.Column(db.String(128))   created_at = db.Column(db.DateTime, default=datetime.utcnow)   def __init__(self, name, email, password):       self.name = name.title()       self.email = email       self.password = password",
        "review": "TODO: в стандартах используется императивный стиль ORM"
    },
    {
        "code": "if not self.is_lecture_attended(course):            self.lecture_attendance.append(course)",
        "review": "TODO: можно вынести часть логики в сервис"
    },
    {
        "code": "sql = f'''           SELECT * FROM table WHERE column = ?           '''\ncursor.execute(sql, [parameter])\nconnection.commit()",
        "review": "TODO: использовать ORM вместо raw-запросов"
    },
    {
        "code": "cursor.execute(f'SELECT * FROM {table}')       connection.commit()",
        "review": "TODO: использовать ORM вместо raw-запросов"
    }
]

def find_similar_reviews_tree(target_codes):
    similar_reviews = []

    # Разделить пути в target_codes на папки
    target_paths = [set(os.path.normpath(code).split(os.sep)) for code in target_codes]

    for review_entry in REVIEWS_TREE:
        review_path = set(os.path.normpath(review_entry["code"]).split(os.sep))
        for target_path in target_paths:
            # Проверить пересечение папок, а также имя файла
            if review_path & target_path and review_entry["code"].split(os.sep)[-1] in target_path:
                similar_reviews.append(f"Code: {review_entry['code']}, Review: {review_entry['review']}")
                break  # Прерываем после нахождения совпадения

    return "\n".join(similar_reviews)  # Возвращаем объединенную строку

def rag_for_tree(request: list):
    # Извлекаем релевантные отзывы из базы
    relevant_reviews = find_similar_reviews_tree(request)

    # Подготавливаем данные для запроса
    url = "http://84.201.152.196:8020/v1/completions"
    headers = {
        "Authorization": "3rL3VN4295xYPlTNMzvt32VGwQl45e1b",
        "Content-Type": "application/json"
    }

    # Формируем запрос с добавлением отзывов из базы
    payload = {
        "model": "mistral-nemo-instruct-2407",
        "messages": [
            {"role": "user", "content": f"Вот дерево проекта: {request}. Сделай Code Review по нему НА РУССКОМ! Вот несколько отзывов из базы по похожим деревьям, которые могут быть полезными: {relevant_reviews}. При ответе не выдумывай! Используй только те отзывы, которые тебе дали! Пиши только про то, что написано плохо! Ответ должнен содержать проблемный участок и отзыв на него!"}
        ],
        "max_tokens": 1024,
        "temperature": 0
    }

    # Отправляем запрос в модель
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def find_similar_reviews_code(file_data):
    # Ищем совпадения
    similar_reviews = []
    for item in REVIEWS_CODE:
        if item["code"] in file_data:
            similar_reviews.append(f"{item['code']} (Отзыв: {item['review']})")

    return ", ".join(similar_reviews)  # Объединяем отзывы в одну строку

def rag_for_code(file_data: string):
    # Извлекаем релевантные отзывы из базы
    relevant_reviews = find_similar_reviews_code(file_data)

    # Подготавливаем данные для запроса
    url = "http://84.201.152.196:8020/v1/completions"
    headers = {
        "Authorization": "3rL3VN4295xYPlTNMzvt32VGwQl45e1b",
        "Content-Type": "application/json"
    }

    # Формируем запрос с добавлением отзывов из базы
    payload = {
        "model": "mistral-nemo-instruct-2407",
        "messages": [
            {"role": "user", "content": f"Вот код файла проекта: {file_data}. Сделай Code Review по нему НА РУССКОМ! Вот несколько отзывов из базы по похожим файлам, которые могут быть полезными: {relevant_reviews}. При ответе не выдумывай! Используй только те отзывы, которые тебе дали! Пиши только про то, что написано плохо! Ответ должнен содержать проблемный участок и отзыв на него!"}
        ],
        "max_tokens": 1024,
        "temperature": 0
    }

    # Отправляем запрос в модель
    response = requests.post(url, headers=headers, json=payload)
    return response.json()