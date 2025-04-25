from application import app
from flask import render_template, redirect, flash, url_for, request, url_for, jsonify,session
from application.models import Customer,Category,db,Product
from flask import request, redirect, url_for, flash, make_response
from flask_jwt_extended import create_access_token, jwt_required,jwt_required, get_jwt_identity, verify_jwt_in_request,decode_token
from application.util import *  
from sqlalchemy import desc
from math import ceil
from datetime import datetime

@app.route("/")
@app.route("/index")
def index(): 
    current_user_id = request.args.get("token")
    user_data= decodeCustomer(current_user_id)
    return render_template("index.html/", title="Home",User=user_data)

@app.route('/userinfo')
@jwt_required(optional=False)  # 必须验证Token
def userinfo():
    current_user_id = get_jwt_identity()  # 获取Token中的用户ID
    user = {
        'username': '人平',
        'status': '不活跃',
        'last_active': '1m 6d',
        'joined': '已注册三年时间',
        'followers': '2个人'
    }
    
    items = [
        {
            'name': '如何使用Carousell交易更安全?',
            'price': 'HK$0',
            'image': 'static/images/carousell_guide.jpg',
            'description': '买家卖家注意！上门交易前请注意',
            'category': '新手指南'
        }
    ]
    return render_template('userInfo.html', user=user, items=items)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # 这里应该从数据库获取产品信息，现在使用模拟数据
    product = {
        'id': product_id,
        'name': '50吋 4K SmartTV SamsungUA50TU8000J WiFi电视',
        'price': 'HK$2,100',
        'seller': {
            'name': '阿伯电器【官方零售店】',
            'rating': 4.8,
            'reviews': 149,
            'image': 'static/images/seller_avatar.jpg'
        },
        'images': ['static/images/tv1.jpg', 'static/images/tv2.jpg', 'static/images/tv3.jpg'],
        'specs': {
            '尺寸': '50吋',
            '屏幕比例': '16:9',
            '品牌': 'SAMSUNG三星',
            '型号': '50TU8000J (122-127.5厘米)',
            '功能': 'WiFi/4K'
        },
        'description': 'Samsung: 50TU8000J',
        'location': '香港新界区/将军澳',
        'address': 'Address: #14 1st Chi Koo Road, Sham Shui Po, Kowloon. (Tai Kok Electric)',
        'contact': '+（852）9146 6667 (Whats-App都可以联系)',
        'delivery_options': ['自取', '送货'],
        'reviews': [
            {
                'user': 'markhan',
                'rating': 5,
                'comment': '私信了，买家很热情',
                'time': '5个月'
            },
            {
                'user': 'chikicam',
                'rating': 5,
                'comment': '好！很好用的，他人也不刁蛮！',
                'time': '7个月'
            }
        ]
    }
    
    # 相关推荐产品
    related_products = [
        {
            'id': 101,
            'name': 'SONY KD-32X75000 索尼 32吋 / 英寸 SMART TV',
            'price': 'HK$1,100',
            'image': 'static/images/related1.jpg'
        },
        {
            'id': 102,
            'name': '43吋 SAMSUNG50800 NEO QLED 4K SMART TV 电视',
            'price': 'HK$3,400',
            'image': 'static/images/related2.jpg'
        }
    ]
    
    return render_template('product_detail.html', product=product, related_products=related_products)

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
    if request.method == 'POST':
        # 处理表单提交逻辑
        title = request.form.get('title')
        price = request.form.get('price')
        description = request.form.get('description')
        # 其他字段处理
        flash('商品已成功发布！', 'success')
        return redirect(url_for('index'))
    
    return render_template('sell.html')



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "用户名和密码是必需的"}), 400

    customer = Customer.query.filter_by(username=username).first()

    if customer and customer.password == password:
        access_token = create_access_token(identity=customer.custID)
        return jsonify({
            "message": "登錄成功",
            "access_token": access_token,
            "expires_in": 3600  # 有效期秒數
        }), 200
        
    else:
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
    district = request.form.get('district') or None
    city = request.form.get('city') or None

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
            district=district,
            city=city,
            website=website,
            email=email,
            bornDate=bornDate
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
    # 只要JWT中间件验证通过即返回成功
    return jsonify({"status": "valid"}), 200


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
    search = request.args.get('search') #搜寻资料
    sort = request.args.get('sort', '最佳匹配')
    product_type = request.args.get('type', '全部')
    style = request.args.get('style', '全部')
    condition = request.args.get('condition', '全部')
    price_range = request.args.get('price', '全部')
    deal_type = request.args.get('deal', '全部')
    category_id = request.args.get('category_id', type=int)
    sort = request.args.get('sort', '最佳匹配')
    circumstance=request.args.get('circumstance', '全部')
    price_range = request.args.get('price_range', '全部')
    
    # products = Product.query.filter(Product.productName.ilike(f'%{search}%')).all()
    now = datetime.utcnow()
    query = db.session.query(Product, Customer).join(Customer)
    if search:
        if category_id!=None:
            query = query.filter(Product.categoryID == category_id)
        else:    
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
                'imagesUrl': product.imagesUrl,
                'multipiece': product.multipiece,
                'handDeliver': product.handDeliver,
                'handDeliverPlace': product.handDeliverPlace,
                'post': product.post,
                'optional_desc': product.optionalDesc,
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
