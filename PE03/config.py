class Config:
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:admin@localhost:5432/DIY Instructions'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
