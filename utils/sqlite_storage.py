from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.configure import Config
from utils.output_log import logger
from utils.minio_storage import upload_file

# ORM setup
engine = create_engine(
    f"sqlite:///{Config.LOCAL_DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Models
class Detail(Base):
    __tablename__ = "Detail"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    account = Column(String)
    date = Column(String)
    post_date = Column(String)
    category = Column(String)
    original_category = Column(String)
    merchant_name = Column(String)
    description = Column(String)
    currency = Column(String, default='CAD')
    amount = Column(Float)

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    api_token = Column(String)

class InputMapping(Base):
    __tablename__ = "InputMapping"
    id = Column(Integer, primary_key=True, index=True)
    account = Column(String)
    source = Column(String)
    target = Column(String)

class CategoryMapping(Base):
    __tablename__ = "CategoryMapping"
    id = Column(Integer, primary_key=True, index=True)
    original_category = Column(String)
    merchant_name = Column(String)
    description = Column(String)
    target_category = Column(String)

# Database initialization
def initialize_db():
    logger.debug("Creating database tables via ORM...")
    Base.metadata.create_all(bind=engine)
    upload_file(Config.LOCAL_DB_PATH, Config.DB_S3_PATH + "main.db")
    logger.info("Database initialized.")

# Session utility
def get_session():
    return SessionLocal()

# Input mapping functions
def get_input_mappings(account):
    logger.debug(f"Fetching input mappings for account: {account}")
    session = get_session()
    mappings = session.query(InputMapping).filter(InputMapping.account == account).all()
    result = {m.target: m.source for m in mappings}
    session.close()
    return result


def save_input_mappings(account, mappings: dict):
    logger.debug(f"Saving input mappings for account: {account}")
    session = get_session()
    session.query(InputMapping).filter(InputMapping.account == account).delete()
    for target, source in mappings.items():
        im = InputMapping(account=account, source=source, target=target)
        session.add(im)
    session.commit()
    session.close()
    upload_file(Config.LOCAL_DB_PATH, Config.DB_S3_PATH + "main.db")
    logger.info(f"Saved input mappings for account {account}")

# Category mapping functions
def get_category_mappings_list():
    logger.debug("Fetching all category mappings")
    session = get_session()
    rows = session.query(CategoryMapping).all()
    session.close()
    return rows


def get_target_category(orig_cat, merchant, description):
    logger.debug(f"Looking up target category for: {orig_cat} | {merchant} | {description}")
    session = get_session()
    mapping = session.query(CategoryMapping).filter(
        CategoryMapping.original_category == orig_cat,
        CategoryMapping.merchant_name == merchant,
        CategoryMapping.description == description
    ).first()
    session.close()
    return mapping.target_category if mapping else ''


def save_category_mapping(orig_cat, merchant, description, target_category):
    logger.debug(f"Saving category mapping: {orig_cat}|{merchant}|{description} -> {target_category}")
    session = get_session()
    cm = CategoryMapping(
        original_category=orig_cat,
        merchant_name=merchant,
        description=description,
        target_category=target_category
    )
    session.add(cm)
    session.query(Detail).filter(
        Detail.original_category == orig_cat,
        Detail.merchant_name == merchant,
        Detail.description == description
    ).update({Detail.category: target_category})
    session.commit()
    session.close()
    upload_file(Config.LOCAL_DB_PATH, Config.DB_S3_PATH + "main.db")
    logger.info(f"Saved category mapping for {orig_cat}|{merchant}|{description}")

# Detail functions
def remove_duplicates(username):
    logger.debug(f"Removing duplicates for user: {username}")
    session = get_session()
    rows = session.query(Detail).filter(Detail.username == username).all()
    seen = set()
    dup_ids = []
    for row in rows:
        key = (row.account, row.date, row.post_date, row.category, row.original_category, row.merchant_name, row.description, row.currency, row.amount)
        if key in seen:
            dup_ids.append(row.id)
        else:
            seen.add(key)
    if dup_ids:
        session.query(Detail).filter(Detail.id.in_(dup_ids)).delete(synchronize_session=False)
        session.commit()
    session.close()
    upload_file(Config.LOCAL_DB_PATH, Config.DB_S3_PATH + "main.db")
    logger.info(f"Removed {len(dup_ids)} duplicate transactions for user {username}")
    return len(dup_ids)


def save_transactions(username, account, df, mappings):
    logger.debug(f"Saving transactions for user {username}, account {account}")
    session = get_session()
    for _, row in df.iterrows():
        category = get_target_category(row.get('original_category', ''), row.get('merchant_name', ''), row.get('description', ''))
        detail = Detail(
            username=username,
            account=account,
            date=row.get('date'),
            post_date=row.get('post_date'),
            category=category,
            original_category=row.get('original_category'),
            merchant_name=row.get('merchant_name'),
            description=row.get('description'),
            currency=row.get('currency', 'CAD'),
            amount=row.get('amount', 0.0),
        )
        session.add(detail)
    session.commit()
    session.close()
    upload_file(Config.LOCAL_DB_PATH, Config.DB_S3_PATH + "main.db")
    logger.info(f"Saved {len(df)} transactions for user {username} and account {account}")

# User functions
def create_user(username, hashed_password, email, api_token):
    logger.debug(f"Creating user: {username}")
    session = get_session()
    user = User(username=username, password=hashed_password, email=email, api_token=api_token)
    session.add(user)
    session.commit()
    session.close()


def get_user(username):
    logger.debug(f"Fetching user: {username}")
    session = get_session()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user


def update_user_token(username, token):
    logger.debug(f"Updating JWT token for user: {username}")
    session = get_session()
    session.query(User).filter(User.username == username).update({User.api_token: token})
    session.commit()
    upload_file(Config.LOCAL_DB_PATH, Config.DB_S3_PATH + "main.db")
    session.close()

def get_all_accounts():
    logger.debug("Fetching all accounts from input mappings")
    session = get_session()
    accounts = [m.account for m in session.query(InputMapping.account).distinct()]
    session.close()
    return accounts