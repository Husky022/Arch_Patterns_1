from iqw_framework.templator import render
from iqw_framework import logger
from patterns.creational_patterns import site
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import Api


logger = logger.Logger('main')

routes = {}

@AppRoute(routes=routes, url='/')
@Debug(name='index')
def index(request):
    print(request)
    return '200 OK', render('index.html', data=request.get('secret', None))

@AppRoute(routes=routes, url='/contacts/')
@Debug(name='contacts')
def contacts(request):
    print(request)
    return '200 OK', render('contacts.html', data=request.get('key', None))

@AppRoute(routes=routes, url='/registration/')
@Debug(name='registration')
def registration(request):
    print(request)
    return '200 OK', render('registration.html', data=request.get('data', None))

@AppRoute(routes=routes, url='/courses/')
@Debug(name='courses')
def courses(request):
    print(request)
    return '200 OK', render('courses.html', courses_list=site.courses)

@AppRoute(routes=routes, url='/course_redactor/')
@Debug(name='course_redactor')
def course_redactor(request):
    print(request)
    return '200 OK', render('course_redactor.html', category_list=site.categories, courses_list=site.courses)

@AppRoute(routes=routes, url='/users/')
@Debug(name='users')
def users(request):
    print(request)
    return '200 OK', render('users.html', category_list=site.categories, courses_list=site.courses, students_list=site.students, teachers_list=site.teachers)

def not_found_404_view(request):
    print(request)
    return '404 WHAT', '404 PAGE Not Found'

def hello_from_fake_view(request):
    print(request)
    return '200 WHAT', 'Hello from Fake'

@AppRoute(routes=routes, url='/api_course/')
def api_site(request):
    print(request)
    return '200 OK', Api(site.courses).convert_to_json()