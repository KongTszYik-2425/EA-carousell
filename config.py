class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://palk:Admin123@rm-cn-fxf459tpy0003foo.rwlb.rds.aliyuncs.com:3306/carousell'  # 换成你的数据库信息
    SQLALCHEMY_COMMIT_ON_TEARDOWN= True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    db = None
