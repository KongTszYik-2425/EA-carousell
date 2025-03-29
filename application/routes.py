from application import app
from flask import render_template, redirect, flash, url_for, request

@app.route("/")
@app.route("/index")
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template("index.html", title="Home", posts=posts)

@app.route('/userinfo')
def userinfo():
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
    
    return render_template('home.html', categories=categories, brands=brands, hot_items=hot_items, zones=zones)

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

