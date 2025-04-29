from application import app
from flask import render_template, redirect, flash, url_for, request, url_for, jsonify,session
from application.models import Customer,Category,db,Product,Review
from flask import request, redirect, url_for, flash, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request, get_jwt
from application.util import *  
from sqlalchemy import desc
from math import ceil
from datetime import datetime,timedelta
from google.cloud import storage
import os
import jwt



@app.route("/")
@app.route("/index")
def index(): 
    one_day_ago = datetime.now() - timedelta(days=1)
    recent_products = Product.query.filter(Product.postDate >= one_day_ago).order_by(desc(Product.postDate)).limit(8).all()
    
    # 为每个商品添加卖家信息和时间信息
    products_with_seller = []
    for product in recent_products:
        seller = Customer.query.get(product.owner)
        
        # 计算上架时间
        time_ago = ""
        if product.postDate:
            now = datetime.now()
            time_diff = now - product.postDate
            
            minutes = int(time_diff.total_seconds() / 60)
            hours = int(minutes / 60)
            days = int(hours / 24)
            
            if minutes < 60:
                time_ago = f"{minutes}分钟前"
            elif hours < 24:
                time_ago = f"{hours}小时前"
            else:
                time_ago = f"{days}天前"
        else:
            time_ago = "未知时间"
        
        product_data = {
            'productID': product.productID,
            'productName': product.productName,
            'price': product.price,
            'avatarUrl': product.avatarUrl,
            'postDate': product.postDate,
            'time_ago': time_ago,  # 添加时间显示
            'praise': product.praise,
            'seller': {
                'username': seller.username if seller else "未知用户",
                'avatarUrl': seller.avatarUrl if seller and hasattr(seller, 'avatarUrl') else "https://media.karousell.com/media/photos/profiles/default_avatar.jpg"
            }
        }
        products_with_seller.append(product_data)
    
    # 查询一周内按点赞数排序的热门商品
    one_week_ago = datetime.now() - timedelta(days=7)
    hot_products = Product.query.filter(Product.postDate >= one_week_ago).order_by(desc(Product.praise)).limit(20).all()
    
    # 为热门商品添加卖家信息和时间信息
    hot_products_with_seller = []
    for product in hot_products:
        seller = Customer.query.get(product.owner)
        
        # 计算上架时间
        time_ago = ""
        if product.postDate:
            now = datetime.now()
            time_diff = now - product.postDate
            
            minutes = int(time_diff.total_seconds() / 60)
            hours = int(minutes / 60)
            days = int(hours / 24)
            
            if minutes < 60:
                time_ago = f"{minutes}分钟前"
            elif hours < 24:
                time_ago = f"{hours}小时前"
            else:
                time_ago = f"{days}天前"
        else:
            time_ago = "未知时间"
        
        product_data = {
            'productID': product.productID,
            'productName': product.productName,
            'price': product.price,
            'avatarUrl': product.avatarUrl,
            'postDate': product.postDate,
            'time_ago': time_ago,
            'praise': product.praise,
            'seller': {
                'username': seller.username if seller else "未知用户",
                'avatarUrl': seller.avatarUrl if seller and hasattr(seller, 'avatarUrl') else "https://media.karousell.com/media/photos/profiles/default_avatar.jpg"
            }
        }
        hot_products_with_seller.append(product_data)

    # 查询所有没有父级的分类（顶级分类）
    

    return render_template(
        "index.html/", 
        title="Home", 
        recent_products=products_with_seller, 
        hot_products=hot_products_with_seller
    )

@app.route("/getTopCategories", methods=['GET', 'POST'])
def getTopCategories():
    top_categories = Category.query.filter_by(parentID=0).limit(5).all()
    
    # 构建分类数据
    categories_data = []
    for category in top_categories:
        category_data = {
            'categoryID': category.categoryID,
            'categoryName': category.categoryName,
            'categoryIcon': category.categoryIcon if hasattr(category, 'categoryIcon') else None
        }
        categories_data.append(category_data)

    return categories_data

@app.route("/getCategories", methods=['GET', 'POST'])
def getCategories():
    all_categories = Category.query.all()
    
    # 创建分类字典，用于快速查找
    category_dict = {category.categoryID: category for category in all_categories}
    
    # 创建分类树结构
    category_tree = []
    
    # 找出所有顶级分类（parentID为0的分类）
    for category in all_categories:
        if category.parentID == 0:
            # 创建分类对象的副本，添加children属性
            category_copy = {
                'categoryID': category.categoryID,
                'categoryName': category.categoryName,
                'parentID': category.parentID,
                'children': []
            }
            category_tree.append(category_copy)
    
    # 将子分类添加到对应的父分类中
    for category in all_categories:
        if category.parentID != 0 and category.parentID in category_dict:
            # 找到父分类在category_tree中的位置
            for parent_category in category_tree:
                if parent_category['categoryID'] == category.parentID:
                    # 创建子分类对象
                    child_category = {
                        'categoryID': category.categoryID,
                        'categoryName': category.categoryName,
                        'parentID': category.parentID
                    }
                    # 添加到父分类的children列表中
                    parent_category['children'].append(child_category)    
    return category_tree                   


@app.route("/getUser")
def getUser():
    user_id = request.args.get('custID')
    print(user_id)
    user_info = Customer.getSimple(user_id)
    return user_info

@app.route('/userinfo')
def userinfo():
    # 获取URL参数中的custID
    cust_id = request.args.get('custID')
    
    # 获取分页和搜索参数
    page = request.args.get('page', 1, type=int)
    review_page = request.args.get('review_page', 1, type=int)  # 添加评价分页参数
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', '')
    per_page = 12  # 每页显示12个产品
    reviews_per_page = 5  # 每页显示5条评价
    
    if not cust_id:
        # 如果没有提供custID，返回错误页面或重定向
        flash('未提供用户ID', 'error')
        return redirect(url_for('index'))
    
    # 查询用户信息
    user_data = Customer.query.get(cust_id)
    
    if not user_data:
        # 如果找不到用户，返回错误页面或重定向
        flash('找不到该用户', 'error')
        return redirect(url_for('index'))
    
    # 计算用户注册时间
    joined_date = user_data.joinDate
    days_since_joined = (datetime.now() - joined_date).days
    
    if days_since_joined > 365:
        joined_text = f'已注册{days_since_joined // 365}年时间'
    else:
        joined_text = f'已注册{days_since_joined}天'
    
    # 查询该用户发布的商品
    products_query = Product.query.filter_by(owner=cust_id)
    
    # 应用搜索过滤
    if search_query:
        products_query = products_query.filter(Product.productName.ilike(f'%{search_query}%'))
    
    # 应用排序
    if sort_by == '最新':
        products_query = products_query.order_by(Product.postDate.desc())
    elif sort_by == '价格从低到高':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == '价格从高到低':
        products_query = products_query.order_by(Product.price.desc())
    else:
        # 默认按最新排序
        products_query = products_query.order_by(Product.postDate.desc())
    
    # 分页
    user_products_pagination = products_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 构建用户信息字典
    user = {
        'custID': user_data.custID,
        'username': user_data.username,
        'status': '活跃' if hasattr(user_data, 'lastLoginDate') and (datetime.now() - user_data.lastLoginDate).days < 7 else '不活跃',
        'last_active': f'{(datetime.now() - user_data.lastLoginDate).days}天' if hasattr(user_data, 'lastLoginDate') else '未知',
        'joined': joined_text,
        'followers': f'{user_data.followers}个人' if hasattr(user_data, 'followers') else '0个人',
        'description': user_data.description if user_data.description else '',
        'avatar': user_data.avatar 
    }
    
    # 构建用户商品列表
    items = []
    for product in user_products_pagination.items:
        item = {
            'productID': product.productID,
            'name': product.productName,
            'praise': product.praise,
            'circumstance': product.circumstance,
            'price': product.price,
            'image': product.avatarUrl,
            'description': product.description[:50] + '...' if product.description and len(product.description) > 50 else product.description,
            'category': Category.query.get(product.categoryID).categoryName if product.categoryID else '未分类',
            'circumstance': product.circumstance,
            'praise': product.praise
        }
        items.append(item)
    
    # 如果用户没有商品，添加一个引导项
    if not items and not search_query:
        items = None
    
    # 计算总页数
    total_pages = user_products_pagination.pages
    
    # 查询用户评价数据
    review_count = Review.query.filter_by(customerID=cust_id).count()
    
    # 计算平均评分
    avg_rating_query = db.session.query(db.func.avg(Review.star)).filter(Review.customerID == cust_id).scalar()
    avg_rating = round(float(avg_rating_query), 1) if avg_rating_query else 0
    # 获取用户的所有评价
    reviews_query = Review.query.filter_by(customerID=cust_id).order_by(Review.reviewDate.desc())
    reviews_pagination = reviews_query.paginate(
        page=review_page, per_page=reviews_per_page, error_out=False
    )
    
    reviews = []
    for review in reviews_pagination.items:
        reviewer = Customer.query.get(review.reviewerID)
        if reviewer:
            # 计算评价时间
            time_ago = ""
            if review.reviewDate:
                now = datetime.now()
                time_diff = now - review.reviewDate
                
                minutes = int(time_diff.total_seconds() / 60)
                hours = int(minutes / 60)
                days = int(hours / 24)
                
                if minutes < 60:
                    time_ago = f"{minutes}分钟前"
                elif hours < 24:
                    time_ago = f"{hours}小时前"
                else:
                    time_ago = f"{days}天前"
            else:
                time_ago = "未知时间"
            
            review_data = {
                'reviewID': review.reviewID,
                'star': review.star,
                'content': review.content,
                'reviewDate': review.reviewDate,
                'time_ago': time_ago,
                'reviewer': {
                    'custID': reviewer.custID,
                    'username': reviewer.username,
                    'avatar': reviewer.avatar if reviewer.avatar else None
                }
            }
            reviews.append(review_data)
    
    return render_template(
        'userInfo.html', 
        user=user, 
        items=items, 
        pagination=user_products_pagination,
        page=page,
        total_pages=total_pages,
        cust_id=cust_id,
        search_query=search_query,
        sort_by=sort_by,
        review_count=review_count,
        avg_rating=avg_rating,
        reviews=reviews,
        reviews_pagination=reviews_pagination,  # 添加评价分页对象
        review_page=review_page  # 添加当前评价页码
    )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # 查询产品信息
    product = Product.query.get_or_404(product_id)
    
    # 查询产品所属分类
    category = Category.query.get(product.categoryID)
    
    # 获取分类的父类信息
    parent_category = None
    if category and category.parentID != 0:
        parent_category = Category.query.get(category.parentID)
    
    # 查询卖家信息
    seller = Customer.query.get(product.owner)
    
    # 查询相关产品（同类别的其他产品）
    related_products = Product.query.filter(
        Product.categoryID == product.categoryID,
        Product.productID != product_id
    ).limit(4).all()
    
    # 构建分类信息字典
    category_info = {
        'current': category.categoryName if category else "未分类",
        'parent': parent_category.categoryName if parent_category else "无父类"
    }
    
    # 解析otherInfo JSON字符串
    other_info = {}
    if product.otherInfo:
        try:
            import json
            other_info = json.loads(product.otherInfo)
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用空字典
            other_info = {}
    
    # 将产品图片URL按分号分割成列表
    product_images = []
    if product.imagesUrl:
        product_images = product.imagesUrl.split(';')
    
    # 查询产品评论及评论用户信息 - 只查询最近的3条评论
    reviews = []
    # 按时间降序排序，取最近的3条评论
    review_query = Review.query.filter_by(customerID=product.owner).order_by(desc(Review.reviewDate)).limit(3).all()
    
    # 计算评论总数
    review_count = Review.query.filter_by(customerID=product.owner).count()
    # 计算平均评分
    avg_rating_query = db.session.query(db.func.avg(Review.star)).filter(Review.customerID == product.owner).scalar()
    avg_rating = round(float(avg_rating_query), 1) if avg_rating_query else 0
    
    for review in review_query:
        # 获取评论用户信息
        reviewer = Customer.query.get(review.reviewerID)
        if reviewer:
            # 计算评论时间
            time_ago = ""
            if review.reviewDate:
                now = datetime.now()
                time_diff = now - review.reviewDate
                
                minutes = int(time_diff.total_seconds() / 60)
                hours = int(minutes / 60)
                days = int(hours / 24)
                
                if minutes < 60:
                    time_ago = f"{minutes}分钟前"
                elif hours < 24:
                    time_ago = f"{hours}小时前"
                else:
                    time_ago = f"{days}天前"
            else:
                time_ago = "未知时间"
                
            review_data = {
                'reviewID': review.reviewID,
                'rating': review.star,
                'comment': review.content   ,
                'reviewDate': review.reviewDate,
                'time_ago': time_ago,  # 添加格式化的时间
                'user': {
                    'custID': reviewer.custID,
                    'username': reviewer.username,
                    'avatarUrl': reviewer.avatar
                }
            }
            reviews.append(review_data)
    
    # 构建卖家信息字典，确保所有需要的字段都包含
    owner_data = {
        'custID': seller.custID,
        'username': seller.username,
        'firstName': seller.firstName,
        'lastName': seller.lastName,
        'gender': seller.gender,
        'description': seller.description,
        'marketPlace': seller.marketPlace,
        'email': seller.email,
        'avatarUrl': seller.avatarUrl if hasattr(seller, 'avatarUrl') else "https://media.karousell.com/media/photos/profiles/2025/02/22/159713332317728_1740213355_19f2911b.jpg"
    }

    product_time = ""
    if product.postDate:
        now = datetime.now()
        create_time = product.postDate
        time_diff = now - create_time
        
        minutes = int(time_diff.total_seconds() / 60)
        hours = int(minutes / 60)
        days = int(hours / 24)
        
        if minutes < 60:
            product_time = f"{minutes}分钟前"
        elif hours < 24:
            product_time = f"{hours}小时前"
        else:
            product_time = f"{days}天前"
    else:
        product_time = "未知时间"
    
    return render_template(
        'product_detail.html', 
        product=product, 
        seller=seller,
        owner=owner_data,  # 添加owner数据
        category_info=category_info,
        related_products=related_products,
        product_images=product_images,
        other_info=other_info,
        reviews=reviews,  # 添加评论数据
        review_count=review_count,  # 添加评论总数
        avg_rating=avg_rating,  # 添加平均评分
        avg_star=round(avg_rating),
        postDate=product_time
    )

@app.route('/home')
def home():
    categories = [
        {'name': 'Mobile Phones & Gadgets', 'icon': 'static/images/category_mobile.png'},
        {'name': 'Video Gaming', 'icon': 'static/images/category_gaming.png'},
        {'name': 'Audio', 'icon': 'static/images/category_audio.png'},
        {'name': 'TV & Home Appliances', 'icon': 'static/images/category_tv.png'},
        {'name': 'Computer & Tech', 'icon': 'static/images/category_computer.png'}
    ]
    
    brands = ['Apple', 'Samsung', 'Sony', 'JBL', 'Dyson', 'LG']
    
    hot_items = [
        {'name': '50吋 4K SmartTV SamsungUA50TU8000J WiFi电视', 'price': 'HK$2,100', 'image': 'static/images/hot_tv.jpg'},
        {'name': 'Apple iPhone 13 Pro Max', 'price': 'HK$9,999', 'image': 'static/images/hot_iphone.jpg'},
        {'name': 'Sony PlayStation 5', 'price': 'HK$4,999', 'image': 'static/images/hot_ps5.jpg'}
    ]
    
    zones = [
        {
            'name': 'Apple Zone',
            'tags': ['iPhone', 'iPad', 'MacBook'],
            'products': [
                {'name': 'Apple iPhone 13 Pro Max', 'price': 'HK$9,999', 'image': 'static/images/apple_iphone.jpg'},
                {'name': 'Apple iPad Pro', 'price': 'HK$7,999', 'image': 'static/images/apple_ipad.jpg'}
            ]
        },
        {
            'name': 'All about computer',
            'tags': ['Laptop', 'Monitor'],
            'products': [
                {'name': 'Dell XPS 13', 'price': 'HK$8,999', 'image': 'static/images/computer_dell.jpg'},
                {'name': 'Apple MacBook Pro', 'price': 'HK$12,999', 'image': 'static/images/computer_macbook.jpg'}
            ]
        },
        {
            'name': 'Smart Phone',
            'tags': ['Mobile', 'Accessories'],
            'products': [
                {'name': 'Samsung Galaxy S21', 'price': 'HK$6,999', 'image': 'static/images/smartphone_samsung.jpg'},
                {'name': 'Google Pixel 6', 'price': 'HK$5,999', 'image': 'static/images/smartphone_pixel.jpg'}
            ]
        }
    ]

    current_user_id = request.args.get("token")
    user_data= decodeCustomer(current_user_id)
    
    return render_template('home.html', categories=categories, brands=brands, hot_items=hot_items, zones=zones,User=user_data)

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    all_categories = Category.query.all()
    # 创建分类字典，用于快速查找
    category_dict = {category.categoryID: category for category in all_categories}
    # 创建分类树结构
    category_tree = []
    # 找出所有顶级分类（parentID为0的分类）
    for category in all_categories:
        if category.parentID == 0:
            # 创建分类对象的副本，添加children属性
            category_copy = {
                'categoryID': category.categoryID,
                'categoryName': category.categoryName,
                'parentID': category.parentID,
                'children': []
            }
            category_tree.append(category_copy)
    
    # 将子分类添加到对应的父分类中
    for category in all_categories:
        if category.parentID != 0 and category.parentID in category_dict:
            # 找到父分类在category_tree中的位置
            for parent_category in category_tree:
                if parent_category['categoryID'] == category.parentID:
                    # 创建子分类对象
                    child_category = {
                        'categoryID': category.categoryID,
                        'categoryName': category.categoryName,
                        'parentID': category.parentID
                    }
                    # 添加到父分类的children列表中
                    parent_category['children'].append(child_category)  


    if request.method == 'POST':
        # 处理表单提交逻辑
        title = request.form.get('title')
        price = request.form.get('price')
        description = request.form.get('description')
        # 其他字段处理
        flash('商品已成功发布！', 'success')
        return redirect(url_for('index'))
    
    return render_template('sell.html',category_tree=category_tree)



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message": "用户名和密码是必需的"}), 400

    customer = Customer.query.filter_by(username=username,password=password).first()
    if customer:
        access_token = create_access_token(identity=customer.custID)
        return jsonify({
            "message": "登錄成功",
            "access_token": access_token,
            "expires_in": 3600  # 有效期秒數
        }), 200
        
    else:
        print("no")
        return jsonify({"message": "用户名或密码错误"}), 401


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    # 确保非必填字段在未传入时为 None
    firstName = request.form.get('firstName') or None
    lastName = request.form.get('lastName') or None
    gender = request.form.get('gender') or None
    description = request.form.get('description') or None
    businessNo = request.form.get('businessNo') or None
    startBusinessTime = request.form.get('startBusinessTime') or None
    endBusinessTime = request.form.get('endBusinessTime') or None
    website = request.form.get('website') or None
    email = request.form.get('email') or None
    bornDate = request.form.get('bornDate') or None
    # 这些是必填字段，确保有值
    marketPlace = request.form.get('marketPlace') or None

    existing_user = Customer.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"status": "error", "message": "用户名已存在，请选择其他用户名。"})
    else:
        new_user = Customer(
            username=username,
            password=password,
            firstName=firstName,
            lastName=lastName,
            gender=gender,
            description=description,
            businessNo=businessNo,
            startBusinessTime=startBusinessTime,
            endBusinessTime=endBusinessTime,
            marketPlace=marketPlace,
            website=website,
            email=email,
            bornDate=bornDate,
            avatar="data:image/png;base64,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"
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success", "message": "注册成功，请前往登录。"})


@app.route('/logout')
def logout():
    pass





@app.route('/auth/check')
@jwt_required()
def check_auth():
    
    user_id = get_jwt_identity()
    user_data= Customer.get(user_id)
    # 只要JWT中间件验证通过即返回成功
    return user_data



# 后台管理路由
@app.route('/admin/dashboard')
def admin_dashboard():
    # 模拟数据
    recent_users = [
        {
            'username': 'Isabella Christensen',
            'description': 'Lorem ipsum is simply...',
            'register_time': '11 MAY 12:56',
            'status': 'active',
            'color': '#4e73df'
        },
        {
            'username': 'Michelle Anderson',
            'description': 'Lorem ipsum is simply text of...',
            'register_time': '11 MAY 10:25',
            'status': 'inactive',
            'color': '#1cc88a'
        },
        {
            'username': 'Karla Sorensen',
            'description': 'Lorem ipsum is simply...',
            'register_time': '9 MAY 17:16',
            'status': 'active',
            'color': '#36b9cc'
        },
        {
            'username': 'Ida Jorgensen',
            'description': 'Lorem ipsum is simply text of...',
            'register_time': '13 MAY 17:46',
            'status': 'inactive',
            'color': '#f6c23e'
        },
        {
            'username': 'Albert Anderson',
            'description': 'Lorem ipsum is simply dummy...',
            'register_time': '21 JULY 12:56',
            'status': 'active',
            'color': '#e74a3b'
        }
    ]
    
    return render_template('admin/dashboard.html', recent_users=recent_users)

@app.route('/admin/users')
@jwt_required()
def admin_users():
    return render_template('admin/users.html')

@app.route('/admin/category')
def admin_category():
    # 获取当前页码，默认为第1页
    page = request.args.get('page', 1, type=int)
    # 每页显示的记录数
    per_page = 10
    
    # 查询总记录数
    total_count = Category.query.count()
    # 计算总页数
    total_pages = ceil(total_count / per_page)
    
    # 查询当前页的数据
    categories_paginate = Category.query.order_by(Category.categoryID).paginate(page=page, per_page=per_page, error_out=False)
    categories = categories_paginate.items
    
    # 获取所有分类，用于下拉选择父类
    all_categories = Category.query.all()
    
    # 为每个分类添加父类名称
    category_dict = {category.categoryID: category.categoryName for category in all_categories}
    
    for category in categories:
        if category.parentID != 0 and category.parentID in category_dict:
            category.parent_name = category_dict[category.parentID]
        else:
            category.parent_name = "无父类"
    
    return render_template('admin/category.html', 
                          categories=categories, 
                          all_categories=all_categories,
                          total_pages=total_pages, 
                          current_page=page,
                          total_count=total_count)

@app.route('/admin/products')
@jwt_required()
def admin_products():
    return render_template('admin/products.html')

@app.route('/admin/orders')
@jwt_required()
def admin_orders():
    return render_template('admin/orders.html')

@app.route('/admin/settings')
@jwt_required()
def admin_settings():
    return render_template('admin/settings.html')


@app.route('/admin/category/add', methods=['POST'])
def add_category():
    category_name = request.form.get('categoryName')
    parent_id = request.form.get('parentID', 0, type=int)
    
    if not category_name:
        flash('分类名称不能为空', 'danger')
        return redirect(url_for('admin_category'))
    
    new_category = Category(
        categoryName=category_name,
        parentID=parent_id
    )
    
    db.session.add(new_category)
    db.session.commit()
    
    flash('分类添加成功', 'success')
    return redirect(url_for('admin_category'))

@app.route('/admin/category/edit', methods=['POST'])
def edit_category():
    category_id = request.form.get('categoryID', type=int)
    category_name = request.form.get('categoryName')
    parent_id = request.form.get('parentID', 0, type=int)
    
    if not category_id or not category_name:
        flash('参数错误', 'danger')
        return redirect(url_for('admin_category'))
    
    category = Category.query.get(category_id)
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('admin_category'))
    
    category.categoryName = category_name
    category.parentID = parent_id
    
    db.session.commit()
    
    flash('分类更新成功', 'success')
    return redirect(url_for('admin_category'))

@app.route('/admin/category/delete', methods=['POST'])
def delete_category():
    category_id = request.form.get('categoryID', type=int)
    
    if not category_id:
        flash('参数错误', 'danger')
        return redirect(url_for('admin_category'))
    
    category = Category.query.get(category_id)
    if not category:
        flash('分类不存在', 'danger')
        return redirect(url_for('admin_category'))
    
    # 检查是否有子分类
    child_categories = Category.query.filter_by(parentID=category_id).count()
    if child_categories > 0:
        flash('该分类下有子分类，无法删除', 'danger')
        return redirect(url_for('admin_category'))
    
    # 检查是否有关联的商品
    products = Product.query.filter_by(categoryID=category_id).count()
    if products > 0:
        flash('该分类下有商品，无法删除', 'danger')
        return redirect(url_for('admin_category'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('分类删除成功', 'success')
    return redirect(url_for('admin_category'))


@app.route('/products')
def product_list():
    current_user_id = request.args.get("token")
    user_data= decodeCustomer(current_user_id)
    # 获取筛选参数
    search =request.args.get('search')#搜寻资料
    sort = request.args.get('sort', '最佳匹配')
    product_type = request.args.get('type', '全部')
    style = request.args.get('style', '全部')
    # condition = request.args.get('condition', '全部')
    price_range = request.args.get('price', '全部')
    deal_type = request.args.get('deal', '全部')
    category_id = request.args.get('category', type=int)
    sort = request.args.get('sort', '最佳匹配')
    circumstance=request.args.get('circumstance', '全部')
    price_range = request.args.get('price_range', '全部')
    
    # products = Product.query.filter(Product.productName.ilike(f'%{search}%')).all()
    now = datetime.utcnow()
    query = db.session.query(Product, Customer).join(Customer)
    
    if search is None:
        search = ''
    
    if category_id:
        query = query.filter(Product.categoryID == category_id)
    if search:    
        query = query.filter(Product.productName.like(f'%{search}%'))

    if sort == '价格从低到高':
        query = query.order_by(Product.price)
    elif sort == '价格从高到低':
        query = query.order_by(desc(Product.price))
    elif sort == '最新发布':
        query = query.order_by(desc(Product.postDate))    

    if circumstance != '全部':
        query = query.filter(Product.circumstance == circumstance)  

    if price_range != '全部':
            if price_range == '0-500':
                query = query.filter(Product.price < 500)
            elif price_range == '500-1000':
                query = query.filter(Product.price >= 500, Product.price < 1000)     
            elif price_range == '1000+':
                query = query.filter(Product.price >=1000)        

    results = query.all()
    new_results = []
    for product, customer in results:
        time_diff = now - product.postDate
        if time_diff.days > 0:
            time_ago = f"{time_diff.days} 天前"
        else:
            hours = int(time_diff.total_seconds() // 3600)
            if hours < 12:
                time_ago = f"✵ {hours} 小时前"
            else:
                time_ago = f"{hours} 小时前"
        result_item = {
                'productID': product.productID,
                'productName': product.productName,
                'categoryID': product.categoryID,
                'circumstance': product.circumstance,
                'price': product.price,
                'avatarUrl': product.avatarUrl,
                'praise': product.praise,
                'post_date': product.postDate,
                'state': product.state,
                'owner': customer.custID,
                'username': customer.username,
                'time_ago': time_ago
            }
        new_results.append(result_item)
    all_categories = Category.query.all()
    
    # 创建分类字典，用于快速查找
    category_dict = {category.categoryID: category for category in all_categories}
    
    # 创建分类树结构
    category_tree = []
    
    # 找出所有顶级分类（parentID为0的分类）
    for category in all_categories:
        if category.parentID == 0:
            # 创建分类对象的副本，添加children属性
            category_copy = {
                'categoryID': category.categoryID,
                'categoryName': category.categoryName,
                'parentID': category.parentID,
                'children': []
            }
            category_tree.append(category_copy)
    
    # 将子分类添加到对应的父分类中
    for category in all_categories:
        if category.parentID != 0 and category.parentID in category_dict:
            # 找到父分类在category_tree中的位置
            for parent_category in category_tree:
                if parent_category['categoryID'] == category.parentID:
                    # 创建子分类对象
                    child_category = {
                        'categoryID': category.categoryID,
                        'categoryName': category.categoryName,
                        'parentID': category.parentID
                    }
                    # 添加到父分类的children列表中
                    parent_category['children'].append(child_category)    
    return render_template('product_list.html', 
                          products=new_results,
                          search=search,
                          sort=sort,
                          saved_search=False,
                          User=user_data,
                          category_tree=category_tree)

@app.route('/uploadProduct', methods=['POST'])
def uploadProduct():
    files = request.files.getlist('preview_images')
    productName = request.form.get('productName')
    price = request.form.get('price')
    circumstance = request.form.get('circumstance')
    description = request.form.get('description')
    categoryID = request.form.get('categoryID')
    deliverMethod = request.form.get('deliverMethod')
    otherInfo = request.form.get('otherInfo')
    owner = request.form.get('owner')

    urls=upload_files_to_bucket(files)
    avatarUrl=urls[0]
    imagesUrl=urls[1]

    new_product = Product(
        productName=productName,
        categoryID=categoryID,
        circumstance=circumstance,
        price=float(price) if price else 0,
        avatarUrl=avatarUrl,
        imagesUrl=imagesUrl,
        otherInfo=otherInfo,  # JSON格式的其他属性
        praise=0,  # 初始点赞数为0
        postDate=datetime.utcnow(),  # 设置当前时间为发布时间
        state="正常",  # 假设1表示正常状态
        owner=owner,  # 设置所有者ID
        description=description,  # 商品描述
        deliverMethod=deliverMethod  # 配送方式：1为面交，0为邮寄
    )
    
    # 将新产品添加到数据库
    db.session.add(new_product)
    db.session.commit()
    
    # 返回成功消息
    return jsonify({
        "status": "success", 
        "message": "产品上传成功", 
        "productID": new_product.productID
    })
    return '上传成功'


@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    # 查询产品
    product = Product.query.get_or_404(product_id)
    # 检查产品是否属于当前用户
    if str(product.owner) != str(current_user_id):
        return jsonify({'message': '您没有权限删除此商品'}), 403
    try:
        if product.avatarUrl and product.avatarUrl.startswith('https://storage.googleapis.com/'):
            try:
                # 从URL中提取文件名
                avatar_filename = product.avatarUrl.split('/')[-1]
                # 删除封面图片
                delete_file_from_bucket(avatar_filename)
            except Exception as e:
                print(f"删除封面图片失败: {str(e)}")
        
        # 删除产品其他图片
        if product.imagesUrl:
            image_urls = product.imagesUrl.split(';')
            for image_url in image_urls:
                if image_url and image_url.startswith('https://storage.googleapis.com/'):
                    try:
                        # 从URL中提取文件名
                        image_filename = image_url.split('/')[-1]
                        # 删除图片
                        delete_file_from_bucket(image_filename)
                    except Exception as e:
                        print(f"删除商品图片失败: {str(e)}")
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': '商品删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

@app.route('/user_edit')
def user_edit():
    return render_template('userEdit.html')

@app.route('/update_user', methods=['POST'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    # 查询用户
    user = Customer.query.get_or_404(current_user_id)
    
    try:
        # 更新基本信息
        user.username = request.form.get('username')
        user.firstName = request.form.get('firstName')
        user.lastName = request.form.get('lastName')
        user.gender = request.form.get('gender')
        user.email = request.form.get('email')
        
        # 处理出生日期
        born_date = request.form.get('bornDate')
        if born_date:
            user.bornDate = datetime.strptime(born_date, '%Y-%m-%d')
        
        # 更新商家信息
        user.description = request.form.get('description')
        user.marketPlace = request.form.get('marketPlace')
        user.businessNo = request.form.get('businessNo')
        user.website = request.form.get('website')
        
        # 处理营业时间
        start_time = request.form.get('startBusinessTime')
        if start_time:
            user.startBusinessTime = datetime.strptime(start_time, '%H:%M').time()
        
        end_time = request.form.get('endBusinessTime')
        if end_time:
            user.endBusinessTime = datetime.strptime(end_time, '%H:%M').time()
       
        # 处理头像上传
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            # 如果用户已有头像，先删除旧头像
            if user.avatar and user.avatar.startswith('https://storage.googleapis.com/'):
                try:
                    # 从URL中提取文件名
                    old_avatar_filename = user.avatar.split('/')[-1]
                    # 删除旧头像
                    delete_file_from_bucket(old_avatar_filename)
                except Exception as e:
                    print(f"删除旧头像失败: {str(e)}")
            # 上传头像到存储服务并获取URL
        avatar_url = upload_file_to_bucket(avatar_file)
        user.avatar = avatar_url
        
        # 保存更改
        db.session.commit()
        
        return jsonify({'message': '用户信息更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

@app.route('/change_password')
def change_password_page():
    return render_template('change_password.html')

@app.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 查询用户
    user = Customer.query.get_or_404(current_user_id)
    
    # 验证当前密码
    current_password = data.get('currentPassword')
    
    if user.password != current_password:
        return jsonify({'message': '当前密码不正确'}), 400
    
    try:
        # 更新密码
        new_password = data.get('newPassword')
        user.password = new_password
        
        # 保存更改
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'密码修改失败: {str(e)}'}), 500        

@app.route('/write_review')
def write_review():
    # 获取要评价的用户ID
    customer_id = request.args.get('custID')
    if not customer_id:
        return redirect('/index')
    
    # 查询用户信息
    user = Customer.query.get_or_404(customer_id)
    
    # 准备用户数据
    user_data = {
        'custID': user.custID,
        'username': user.username,
        'avatar': user.avatar
    }
    
    return render_template('write_review.html', user=user_data)

@app.route('/submit_review', methods=['POST'])
@jwt_required()
def submit_review():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 获取评价数据
    customer_id = data.get('customerID')
    rating = data.get('rating')
    content = data.get('content')
    
    # 验证数据
    if not customer_id or not rating or not content:
        return jsonify({'message': '缺少必要的评价信息'}), 400
    
    # 验证不能评价自己
    if str(current_user_id) == str(customer_id):
        return jsonify({'message': '不能评价自己'}), 400
    
    try:
        # 创建新评价
        new_review = Review(
            customerID=customer_id,
            reviewerID=current_user_id,
            star=rating,
            content=content,
            reviewDate=datetime.now()
        )
        
        # 保存到数据库
        db.session.add(new_review)
        db.session.commit()
        
        return jsonify({'message': '评价提交成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'评价提交失败: {str(e)}'}), 500