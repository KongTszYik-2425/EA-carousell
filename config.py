class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Admin123@db:3306/carousell'  # 换成你的数据库信息
    SQLALCHEMY_COMMIT_ON_TEARDOWN= True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'helloworld'
    db = None
    
