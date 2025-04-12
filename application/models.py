from datetime import datetime

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
    district = db.Column(db.String(100), nullable=False, comment='地区')
    city = db.Column(db.String(100), nullable=False, comment='城市')
    website = db.Column(db.String(100), nullable=True, comment='网页链接')
    email = db.Column(db.String(100), nullable=True)
    bornDate = db.Column(db.Date, nullable=True)
    joinDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='注册时间')
    Avatar = db.Column(db.String(100), nullable=True, comment='头像')
    coin = db.Column(db.Float, nullable=False, default=0, comment='特殊币')
    currency = db.Column(db.Float, nullable=False, default=0, comment='现金')
    password = db.Column(db.String(100), nullable=False)

    # 返回函数
    def __repr__(self):
        return f'<Customer {self.username}>'


class Comment(db.Model):
    __tablename__ = 'comment'

    commentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customerID = db.Column(db.Integer, nullable=False, comment='卖家ID')
    content = db.Column(db.Text, nullable=True)
    star = db.Column(db.Integer, nullable=False, default=0, comment='打星')
    criticID = db.Column(db.Integer, nullable=False, comment='评论者ID')
    commentDate = db.Column(db.DateTime, nullable=False, comment='评论时间')

    def __repr__(self):
        return f'<Comment {self.commentID} by {self.criticID}>'


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
    condition = db.Column(db.String(100), nullable=False, comment='商品状况')
    price = db.Column(db.Float, nullable=False)
    avatarUrl = db.Column(db.String(100), nullable=False, comment='封面')
    imagesUrl = db.Column(db.Text, nullable=True)
    multipiece = db.Column(db.Boolean, nullable=False, default=0, comment='是否多件')
    handDeliver = db.Column(db.Boolean, nullable=False, default=0, comment='是否面交')
    handDeliverPlace = db.Column(db.String(100), nullable=True, comment='面交地点')
    post = db.Column(db.Boolean, default=1, comment='是否邮寄')
    optionalDesc = db.Column(db.Text, nullable=True, comment='选择性填写资料')
    praise = db.Column(db.Integer, nullable=False, default=0, comment='点赞数量')

    def __repr__(self):
        return f'<Product {self.productName}>'
