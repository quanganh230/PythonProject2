import base64
from io import BytesIO
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import collection, ConcreteDevice

def dashboard_view(request):
    devices = list(collection.find({"is_active": True}))
    return render(request, 'devices/dashboard.html', {'devices': devices})

def add_device_view(request):
    if request.method == "POST":
        try:
            d_id = request.POST.get('device_id')
            name = request.POST.get('device_name')
            price = float(request.POST.get('purchase_price'))
            brand = request.POST.get('brand')
            warranty = int(request.POST.get('warranty_months'))
            device = ConcreteDevice(d_id, name, price, brand, warranty)

            if device.sync_to_storage():
                messages.success(request, "Thêm thiết bị thành công!")
                return redirect('dashboard')
            else:
                messages.error(request, "Lỗi khi đồng bộ vào cơ sở dữ liệu.")
        except ValueError as ve:
            messages.error(request, f"Dữ liệu không hợp lệ: {ve}")
        except Exception as e:
            messages.error(request, f"Đã xảy ra lỗi: {e}")

    return render(request, 'devices/add_device.html')

def search_view(request):
    query = request.GET.get('q', '')
    if query:
        # Tìm kiếm theo Tên hoặc Thương hiệu
        devices = list(collection.find({
            "is_active": True,
            "$or": [
                {"device_name": {"$regex": query, "$options": "i"}},
                {"brand": {"$regex": query, "$options": "i"}}
            ]
        }))
    else:
        devices = list(collection.find({"is_active": True}))
    return render(request, 'devices/dashboard.html', {'devices': devices, 'query': query})

def delete_device_view(request, device_id):
    collection.delete_one({"device_id": device_id})
    messages.success(request, f"Đã xóa thiết bị {device_id} thành công.")
    return redirect('dashboard')

def charts_view(request):
    devices = list(collection.find({"is_active": True}))
    if not devices:
        return render(request, 'devices/charts.html', {'pie_chart': None, 'bar_chart': None})

    brand_counts = {}
    brand_prices = {}

    for d in devices:
        b = d.get('brand', 'Unknown')
        p = d.get('purchase_price', 0.0)

        brand_counts[b] = brand_counts.get(b, 0) + 1
        brand_prices.setdefault(b, []).append(p)

    plt.figure(figsize=(5, 5))
    plt.pie(brand_counts.values(), labels=brand_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Tỷ lệ thiết bị theo Thương hiệu")

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    pie_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    brand_avg_prices = {b: sum(p_list) / len(p_list) for b, p_list in brand_prices.items()}

    plt.figure(figsize=(6, 5))
    plt.bar(brand_avg_prices.keys(), brand_avg_prices.values(), color='skyblue')
    plt.xlabel("Thương hiệu")
    plt.ylabel("Giá trung bình ($)")
    plt.title("Giá mua trung bình theo Thương hiệu")

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    bar_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    context = {
        'pie_chart': pie_base64,
        'bar_chart': bar_base64
    }
    return render(request, 'devices/charts.html', context)