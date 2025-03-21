from application.customer import customer
from flask import request
from application import models
import config
from datetime import datetime
@customer.route('/')
def index():
    return 'hello'


@customer.route('/login', methods=['POST'])
def login():
    name = request.form.get('name')
    password=request.form.get('password')

@customer.route('/getAllUsers')
def get_all_users():
    customers = models.Customer.query.all() # 查询所有客户
    customer_list = [str(customer) for customer in customers]  # 将每个实例转换为字符串
    print(customer_list)
    return '<br>'.join(str(customer_list))  # 返回所有客户的字符串


@customer.route('/insert_customers')
def insert_customers():
    # 创建一些 Customer 实例
    customer1 = models.Customer(
        username='alice',
        firstName='Alice',
        lastName='Wang',
        gender='F',
        description='A regular customer.',
        businessNo='123456789',
        startBusinessTime='09:00:00',
        endBusinessTime='17:00:00',
        marketPlace='Downtown',
        district='Central',
        city='CityA',
        website='http://alice.com',
        email='alice@example.com',
        bornDate='1990-01-01',
        joinDate=datetime.utcnow(),
        Avatar='http://example.com/avatar/alice.jpg',
        coin=10.0,
        currency=100.0,
        password='password123'
    )

    customer2 = models.Customer(
        username='bob',
        firstName='Bob',
        lastName='Smith',
        gender='M',
        description='A loyal customer.',
        businessNo='987654321',
        startBusinessTime='10:00:00',
        endBusinessTime='18:00:00',
        marketPlace='Uptown',
        district='North',
        city='CityB',
        website='http://bob.com',
        email='bob@example.com',
        bornDate='1985-05-05',
        joinDate=datetime.utcnow(),
        Avatar='http://example.com/avatar/bob.jpg',
        coin=20.0,
        currency=200.0,
        password='password456'
    )

    # 添加到会话中并提交
    config.Config.db.session.add(customer1)
    config.Config.db.session.add(customer2)
    config.Config.db.session.commit()

    return 'Inserted customers successfully!'
