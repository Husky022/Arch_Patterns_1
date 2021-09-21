import quopri
from wsgiref.util import setup_testing_defaults
import views
from datetime import datetime


from patterns.creational_patterns import site, CourseMapper, connection, MapperRegistry, observable, StudentMapper
from iqw_framework.logger import Logger
from patterns.architectural_patterns import UnitOfWork


UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)
logger = Logger('main')


class Framework():
    def __init__(self, routes, fronts):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):
        setup_testing_defaults(environ)
        print(environ)
        path = environ['PATH_INFO']
        if path == '/index.html':
            path ='/'
        if path.endswith('.html'):
            path = path.rstrip('.html')
        if not path.endswith('/'):
            path += '/'

        request = {}

        method = environ['REQUEST_METHOD']

#### Проблемный кусок кода (начало)
        if method == 'GET':
            #Добавил здесь просто вывод данных в терминал, могу также добавить вывод в файл, если требуется
            print(f'{datetime.now()} - GET запрос, данные запроса - {self.handler_data(environ["QUERY_STRING"])}')
        if method == 'POST':
            data_from_post = self.data_decoder(self.wsgi_input_data(environ))
            if 'new_category' in data_from_post:
                new_category = site.create_category(data_from_post['new_category'])
                logger.log(f'добавлена категория {data_from_post["new_category"]}')
                new_category.mark_new()
            if 'new_course' in data_from_post:
                new_course = site.create_course(data_from_post['format'], data_from_post['new_course'],
                                                                      data_from_post['category_course'],
                                                                      data_from_post['address'])
                logger.log(f'добавлен новый курс {new_course.name}({new_course.category})')
                new_course.mark_new()
                users_to_notify_mapper = StudentMapper(connection)
                users_to_notify = users_to_notify_mapper.all()
                for user in users_to_notify:
                    observable.notify(new_course.name, user)
            if 'copy-course' in data_from_post:
                pass
            if 'del-course' in data_from_post:
                course_mapper = CourseMapper(connection)
                course_remove = course_mapper.find_by_id(data_from_post['del-course'])
                logger.log(f'удален курс {course_remove.name}, ID - {course_remove.id}')
                course_remove.mark_removed()
            if 'new-user' in data_from_post:
                new_user = site.create_user(data_from_post['user-type'], data_from_post['new-user'], data_from_post['gender'], data_from_post['date_of_birth'])
                logger.log(f'добавлен пользователь {data_from_post["new-user"]}({data_from_post["user-type"]})')
                new_user.mark_new()
            if 'signing_student' in data_from_post:
                pass
                # for course in site.courses:
                #     if data_from_post['signing_student_course'] == course.name:
                #         if data_from_post['signing_student'] not in course.students:
                #             course.students.append(data_from_post['signing_student'])
            if 'signing_teacher' in data_from_post:
                pass
                # for course in site.courses:
                #     if data_from_post['signing_teacher_course'] == course.name:
                #         if data_from_post['signing_teacher'] not in course.teachers:
                #             course.teachers.append(data_from_post['signing_teacher'])
            print(f'{datetime.now()} - POST запрос, данные запроса - {data_from_post}')
            UnitOfWork.get_current().commit()
#### Проблемный кусок кода (конец)

        if path in self.routes:
            view = self.routes[path]
        else:
            view = views.not_found_404_view
        for front in self.fronts:
            front(request)
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]


    def handler_data(self, data):
        result = {}
        if data:
            params = data.split('&')
            for item in params:
                k, v = item.split('=')
                result[k] = v
        return result


    def wsgi_input_data(self, env):
        content_length_data = env['CONTENT_LENGTH']
        content_length = int(content_length_data)
        data = env['wsgi.input'].read(content_length)
        return data


    def data_decoder(self, data):
        result = {}
        if data:
            data_str = data.decode(encoding='utf-8')
            handling_data = self.handler_data(data_str)
            for k, v in handling_data.items():
                val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
                val_decode_str = quopri.decodestring(val).decode('UTF-8')
                result[k] = val_decode_str
        return result


class LogFramework(Framework):
    def __init__(self, environ, start_response):
        self.application = Framework(environ, start_response)
        super().__init__(environ, start_response)

    def __call__(self, environ, start_response):
        print(f'Метод запроса {environ["REQUEST_METHOD"]}')
        print(f'Данные запроса {environ}')
        return Framework(environ, start_response)

class FakeFramework(Framework):

    def __init__(self, environ, start_response):
        self.application = Framework(environ, start_response)
        super().__init__(environ, start_response)

    def __call__(self, environ, start_response):
        request = {}
        view = views.hello_from_fake_view
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]
