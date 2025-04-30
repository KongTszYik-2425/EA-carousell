from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request, get_jwt
from flask_sqlalchemy import SQLAlchemy
import hashlib
import config

db = config.Config.db


class Customer(db.Model):
    __tablename__ = 'customer'

    custID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    firstName = db.Column(db.String(100), nullable=True)
    lastName = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(1), nullable=True)
    description = db.Column(db.Text, nullable=True)
    businessNo = db.Column(db.String(100), nullable=True, comment='商业号码')
    startBusinessTime = db.Column(db.Time, nullable=True, comment='开始营业时间')
    endBusinessTime = db.Column(db.Time, nullable=True, comment='结束营业时间')
    marketPlace = db.Column(db.String(100), nullable=False, comment='营业地点')
    website = db.Column(db.String(100), nullable=True, comment='网页链接')
    email = db.Column(db.String(100), nullable=True)
    bornDate = db.Column(db.Date, nullable=True)
    joinDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='注册时间')
    avatar = db.Column(db.Text, nullable=True, comment='头像')
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, comment='是否为管理员')
    state=db.Column(db.String(10),nullable=False,default='正常',comment='状态')
    products = db.relationship('Product', backref='customer', lazy='dynamic')

    def get(current_user_id):
        user_data = None
        if current_user_id:
            user = Customer.query.get(current_user_id)
            if user:
                    user_data = {
                        'custID': user.custID,
                        'username': user.username,
                        'gender': user.gender,
                        'description': user.description,
                        'businessNo': user.businessNo,
                        'startBusinessTime': user.startBusinessTime.strftime('%H:%M') if user.startBusinessTime else None,
                        'endBusinessTime': user.endBusinessTime.strftime('%H:%M') if user.endBusinessTime else None,
                        'marketPlace': user.marketPlace,
                        'website': user.website,
                        'email': user.email,
                        'bornDate': user.bornDate.strftime('%Y-%m-%d') if user.bornDate else None,
                        'joinDate': user.joinDate.strftime('%Y-%m-%d %H:%M:%S') if user.joinDate else None,
                        'avatar': user.avatar,
                        'is_admin': user.is_admin,
                        'state':user.state
                    }
        return user_data    

    def getSimple(current_user_id):
        user_data = None
        if current_user_id:
                user = Customer.query.get(current_user_id)
                if user:
                    user_data = {
                        'custID': user.custID,
                        'username': user.username,
                        'gender': user.gender,
                        'description': user.description,
                        'businessNo': user.businessNo,
                        'startBusinessTime': user.startBusinessTime.strftime('%H:%M') if user.startBusinessTime else None,
                        'endBusinessTime': user.endBusinessTime.strftime('%H:%M') if user.endBusinessTime else None,
                        'marketPlace': user.marketPlace,
                        'website': user.website,
                        'email': user.email,
                        'bornDate': user.bornDate.strftime('%Y-%m-%d') if user.bornDate else None,
                        'joinDate': user.joinDate.strftime('%Y-%m-%d %H:%M:%S') if user.joinDate else None,
                        'avatar': user.avatar,
                        'is_admin': user.is_admin,
                        'state':user.state
                    }
        return user_data    
    # 返回函数
    def __repr__(self):
        return f'<Customer {self.username}>'


class Category(db.Model):
    __tablename__ = 'category'

    categoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoryName = db.Column(db.String(100), nullable=False)
    parentID = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Category {self.categoryName}>'


class Product(db.Model):
    __tablename__ = 'product'

    productID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productName = db.Column(db.String(100), nullable=False)
    categoryID = db.Column(db.Integer, nullable=False, comment='类id')
    circumstance = db.Column(db.String(100), nullable=False, comment='商品状况')
    price = db.Column(db.Float, nullable=False)
    avatarUrl = db.Column(db.String(100), nullable=False, comment='封面')
    imagesUrl = db.Column(db.Text, nullable=True)
    otherInfo = db.Column(db.Text, nullable=True, comment='选择性填写资料')
    praise = db.Column(db.Integer, nullable=False, default=0, comment='点赞数量')
    postDate = db.Column(db.DateTime, nullable=False, comment='发布时间')
    state = db.Column(db.String(100), nullable=False, default=0, comment='商品状态:正常,下架,冻结')
    owner=db.Column(db.Integer,db.ForeignKey('customer.custID'),nullable=False,comment='卖家id')
    description = db.Column(db.Text, nullable=True, comment='描述')
    deliverMethod=db.Column(db.String(50),nullable=True,comment='配送方式')
    def __repr__(self):
        return f'<Product {self.productName}>'


class Review(db.Model):
    __tablename__ = 'review'        

    reviewID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customerID = db.Column(db.Integer, nullable=False, comment='被评价的用户ID')
    reviewerID = db.Column(db.Integer, nullable=False, comment='评价者ID')
    content = db.Column(db.Text, nullable=False, comment='评价内容')
    star = db.Column(db.Integer, nullable=False, default=0, comment='评分(1-5星)')
    reviewDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='评价时间')
    
    # 添加外键关联
    customer = db.relationship('Customer', foreign_keys=[customerID], 
                              backref=db.backref('received_reviews', lazy='dynamic'),
                              primaryjoin="Review.customerID == Customer.custID")
    
    reviewer = db.relationship('Customer', foreign_keys=[reviewerID],
                              backref=db.backref('given_reviews', lazy='dynamic'),
                              primaryjoin="Review.reviewerID == Customer.custID")

    def __repr__(self):
        return f'<Review {self.reviewID} from {self.reviewerID} to {self.customerID}>'
