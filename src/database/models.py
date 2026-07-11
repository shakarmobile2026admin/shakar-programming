from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey,
    Enum, Date, Numeric, UniqueConstraint, Index, CheckConstraint, DECIMAL
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """نقش‌های کاربران"""
    ADMIN = "admin"
    MANAGER = "manager"
    SELLER = "seller"
    ACCOUNTANT = "accountant"
    VIEWER = "viewer"


class PaymentMethod(str, enum.Enum):
    """روش‌های پرداخت"""
    CASH = "cash"
    CARD = "card"
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"
    INSTALLMENT = "installment"


class TransactionType(str, enum.Enum):
    """نوع تراکنش"""
    SALE = "sale"
    RETURN = "return"
    PURCHASE = "purchase"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class DocumentStatus(str, enum.Enum):
    """وضعیت اسناد"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    CANCELLED = "cancelled"


# ================== مدل‌های کاربر و احراز هویت ==================

class User(Base):
    """مدل کاربر"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    branch = relationship("Branch", back_populates="users")
    activities = relationship("ActivityLog", back_populates="user")
    sales = relationship("Sale", back_populates="seller")


class Branch(Base):
    """مدل شعبه"""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_main = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    users = relationship("User", back_populates="branch")
    inventory = relationship("Inventory", back_populates="branch")
    sales = relationship("Sale", back_populates="branch")
    purchases = relationship("Purchase", back_populates="branch")
    accounts = relationship("Account", back_populates="branch")
    cash_registers = relationship("CashRegister", back_populates="branch")


# ================== مدل‌های محصول و دسته‌بندی ==================

class Category(Base):
    """مدل دسته‌بندی"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    products = relationship("Product", back_populates="category")


class Product(Base):
    """مدل محصول"""
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint('barcode', name='unique_barcode'),
        CheckConstraint('purchase_price >= 0', name='check_purchase_price'),
        CheckConstraint('sale_price >= 0', name='check_sale_price'),
    )

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    
    # قیمت‌ها
    purchase_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    sale_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    wholesale_price = Column(DECIMAL(15, 2), nullable=True)
    
    # موجودی
    min_stock = Column(Integer, default=5)
    max_stock = Column(Integer, default=1000)
    reorder_quantity = Column(Integer, default=50)
    
    # حالت
    is_active = Column(Boolean, default=True)
    is_taxable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")


class Inventory(Base):
    """مدل موجودی انبار"""
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint('product_id', 'branch_id', name='unique_product_branch'),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)  # موجودی رزرو شده
    last_count_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    product = relationship("Product", back_populates="inventory")
    branch = relationship("Branch", back_populates="inventory")


# ================== مدل‌های فروش و خرید ==================

class Sale(Base):
    """مدل فروش"""
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    
    # مبالغ
    subtotal = Column(DECIMAL(15, 2), default=0)  # جمع کل بدون تخفیف و مالیات
    discount_amount = Column(DECIMAL(15, 2), default=0)  # مبلغ تخفیف
    tax_amount = Column(DECIMAL(15, 2), default=0)  # مبلغ مالیات
    total_amount = Column(DECIMAL(15, 2), default=0)  # جمع کل
    paid_amount = Column(DECIMAL(15, 2), default=0)  # مبلغ پرداخت شده
    remaining_amount = Column(DECIMAL(15, 2), default=0)  # مبلغ باقی مانده
    
    # شرایط
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    description = Column(Text, nullable=True)
    
    # دسته‌بندی
    transaction_type = Column(Enum(TransactionType), default=TransactionType.SALE)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    branch = relationship("Branch", back_populates="sales")
    seller = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale")


class SaleItem(Base):
    """مدل ردیف فروش"""
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    discount_percent = Column(Float, default=0)  # درصد تخفیف
    discount_amount = Column(DECIMAL(15, 2), default=0)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    
    # روابط
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class Purchase(Base):
    """مدل خرید"""
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    purchase_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    
    # مبالغ
    subtotal = Column(DECIMAL(15, 2), default=0)
    discount_amount = Column(DECIMAL(15, 2), default=0)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    total_amount = Column(DECIMAL(15, 2), default=0)
    paid_amount = Column(DECIMAL(15, 2), default=0)
    remaining_amount = Column(DECIMAL(15, 2), default=0)
    
    # شرایط
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    branch = relationship("Branch", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="purchase")


class PurchaseItem(Base):
    """مدل ردیف خرید"""
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    discount_percent = Column(Float, default=0)
    discount_amount = Column(DECIMAL(15, 2), default=0)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    
    # روابط
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")


# ================== مدل‌های مشتری و تامین‌کننده ==================

class Customer(Base):
    """مدل مشتری"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(50), nullable=False)
    
    # اطلاعات مالی
    credit_limit = Column(DECIMAL(15, 2), default=0)  # سقف اعتباری
    current_debt = Column(DECIMAL(15, 2), default=0)  # بدهی فعلی
    discount_percent = Column(Float, default=0)  # درصد تخفیف
    
    # حالت
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    sales = relationship("Sale", back_populates="customer")


class Supplier(Base):
    """مدل تامین‌کننده"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(50), nullable=False)
    bank_account = Column(String(50), nullable=True)
    
    # اطلاعات مالی
    total_purchase = Column(DECIMAL(15, 2), default=0)
    current_debt = Column(DECIMAL(15, 2), default=0)
    discount_percent = Column(Float, default=0)
    
    # حالت
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    purchases = relationship("Purchase", back_populates="supplier")


# ================== مدل‌های پرداخت و چک ==================

class Payment(Base):
    """مدل پرداخت"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(DECIMAL(15, 2), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # ارتباط با سند
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'), nullable=True)
    
    # شرح اضافی
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    sale = relationship("Sale", back_populates="payments")
    purchase = relationship("Purchase", back_populates="payments")


class Check(Base):
    """مدل چک"""
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    check_number = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(DECIMAL(15, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    bank_name = Column(String(100), nullable=False)
    issue_date = Column(Date, default=datetime.utcnow)
    
    # حالت چک
    status = Column(String(20), default="pending")  # pending, cleared, returned, cancelled
    
    # ارتباط
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ================== مدل‌های حسابداری ==================

class Account(Base):
    """مدل حساب (برای حسابداری دوجانبه)"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    account_type = Column(String(30), nullable=False)  # asset, liability, equity, revenue, expense
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)  # حساب بالاسری
    
    # موازنه
    balance = Column(DECIMAL(15, 2), default=0)
    
    # حالت
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    branch = relationship("Branch", back_populates="accounts")
    journal_entries = relationship("JournalEntry", back_populates="account")


class JournalEntry(Base):
    """مدل دفتر روزنامه"""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    entry_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # بدهکار و بستانکار
    debit = Column(DECIMAL(15, 2), default=0)  # بدهکار
    credit = Column(DECIMAL(15, 2), default=0)  # بستانکار
    
    # توضیح
    description = Column(Text, nullable=True)
    reference_document = Column(String(50), nullable=True)  # شماره سند مرجع
    
    # حالت
    is_posted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    account = relationship("Account", back_populates="journal_entries")


# ================== مدل‌های صندوق ==================

class CashRegister(Base):
    """مدل صندوق"""
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    
    # موجودی
    opening_balance = Column(DECIMAL(15, 2), default=0)
    current_balance = Column(DECIMAL(15, 2), default=0)
    
    # حالت
    is_active = Column(Boolean, default=True)
    is_open = Column(Boolean, default=False)  # صندوق باز است یا بسته
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    branch = relationship("Branch", back_populates="cash_registers")


# ================== مدل‌های لاگ و فعالیت ==================

class ActivityLog(Base):
    """مدل ثبت فعالیت"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)  # create, update, delete, login, logout
    entity_type = Column(String(50), nullable=False)  # Sale, Purchase, Product, etc
    entity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # روابط
    user = relationship("User", back_populates="activities")


class SystemLog(Base):
    """مدل لاگ سیستم"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    traceback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ایجاد ایندکس برای بهبود کارایی
Index('idx_sale_date', Sale.date)
Index('idx_purchase_date', Purchase.date)
Index('idx_product_barcode', Product.barcode)
Index('idx_inventory_product_branch', Inventory.product_id, Inventory.branch_id)
Index('idx_activity_log_date', ActivityLog.created_at)
