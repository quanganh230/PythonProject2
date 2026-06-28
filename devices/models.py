from typing import Protocol, List
import math
from datetime import datetime
from django.db import models
from pymongo import MongoClient

class DeviceProtocol(Protocol):
    device_id: str
    device_name: str
    purchase_price: float
    brand: str
    warranty_months: int

    def show_device_details(self) -> None: ...

    def calculate_depreciation(years: int) -> float: ...

    def update_warranty(new_months: int) -> bool: ...

    def sync_to_storage(self) -> bool: ...

    @staticmethod
    def filter_by_brand(brand_name: str) -> list: ...
client = MongoClient("mongodb://localhost:27017/")
db = client["device_db"]
collection = db["devices_collection"]


class ConcreteDevice:
    def __init__(self, device_id: str = None, device_name: str = None,
                 purchase_price: float = None, brand: str = None, warranty_months: int = None):

        if device_id is not None:
            if len(device_id) != 12:
                raise ValueError("device_id phải có độ dài chính xác 12 ký tự.")
            if purchase_price <= 0:
                raise ValueError("purchase_price phải lớn hơn 0.")
            if warranty_months < 0:
                raise ValueError("warranty_months phải lớn hơn hoặc bằng 0.")

        self.device_id = device_id if device_id else ""
        self.device_name = device_name if device_name else ""
        self.purchase_price = purchase_price if purchase_price else 0.0
        self.brand = brand if brand else ""
        self.warranty_months = warranty_months if warranty_months else 0

    def show_device_details(self) -> None:
        print("=" * 40)
        print(f"THÔNG TIN THIẾT BỊ: {self.device_name.upper()}")
        print("=" * 40)
        print(f"- Mã thiết bị   : {self.device_id}")
        print(f"- Thương hiệu   : {self.brand}")
        print(f"- Giá mua       : ${self.purchase_price:,.2f}")
        print(f"- Hạn bảo hành  : {self.warranty_months} tháng")
        print("=" * 40)

    def calculate_depreciation(self, years: int) -> float:
        return round(self.purchase_price * math.pow(0.9, years), 2)

    def update_warranty(self, new_months: int) -> bool:
        if new_months < self.warranty_months:
            return False
        self.warranty_months = new_months
        return True

    def sync_to_storage(self) -> bool:
        try:
            device_data = {
                "device_id": self.device_id,
                "device_name": self.device_name,
                "purchase_price": self.purchase_price,
                "brand": self.brand,
                "warranty_months": self.warranty_months,
                "entry_date": datetime.now(),
                "is_active": True
            }
            collection.update_one({"device_id": self.device_id}, {"$set": device_data}, upsert=True)
            return True
        except Exception as e:
            print(f"Lỗi đồng bộ MongoDB: {e}")
            return False

    @staticmethod
    def filter_by_brand(brand_name: str) -> list:
        try:
            results = collection.find({"brand": {"$regex": brand_name, "$options": "i"}})
            return list(results)
        except Exception as e:
            print(f"Lỗi truy vấn MongoDB: {e}")
            return []

class DeviceModel(models.Model):
    device_id = models.CharField(max_length=12, unique=True)
    device_name = models.CharField(max_length=255)
    purchase_price = models.FloatField()
    brand = models.CharField(max_length=100)
    warranty_months = models.IntegerField()
    entry_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"