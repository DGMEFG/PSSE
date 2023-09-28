from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Car, ParkingRecord, ParkingRate, GlobalSettings
from management.permissions import is_admin
import math
import json
# Create your views here.

def calculate_parking_duration(start_time, end_time):
    # 计算停车时间（以分钟为单位）
    if start_time and end_time:
        duration = (end_time - start_time).total_seconds() / 60
        return duration
    return 0

def calculate_parking_price(parking_duration_minutes, car_type):
    try:
        # 尝试从数据库中获取给定车型的价格记录
        parking_rate = ParkingRate.objects.get(car_type=car_type)
        
        # 获取价格记录中的价格信息
        rate_per_hour = parking_rate.price_per_hour

        # 计算停车价格，四舍五入到两位小数
        parking_price = round((math.ceil(parking_duration_minutes / 60)) * rate_per_hour, 2)

        return parking_price
    except ParkingRate.DoesNotExist:
        # 如果车型不存在对应的价格记录，可以返回一个默认价格或者引发异常
        raise ValueError('未知的车型')



@login_required
@csrf_exempt
def add_car(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        car_type = data.get('car_type')
        user = request.user
        if not user:
            return JsonResponse({'success': False, 'error': '用户未登录'}, status=401)

        license_plate = data.get('license_plate')
        existing_car = Car.objects.filter(license_plate=license_plate).first()
        if existing_car:
            return JsonResponse({'success': True, 'message': '车辆已存在'}, status=200)

        park = data.get('park', False)
        if park:
            parked_at = timezone.now()
        else:
            parked_at = None
        # 创建车辆并设置停车时间为空
        car = Car.objects.create(license_plate=license_plate, parked_at=parked_at,car_type=car_type)

        # 将车辆与用户关联
        user.cars.add(car)

        return JsonResponse({'success': True, 'message': '车辆已添加'}, status=201)
    else:
        return JsonResponse({'success': False, 'error': '只允许POST请求'}, status=400)
    
@login_required
@csrf_exempt
def park_car(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user = request.user
        if not user:
            return JsonResponse({'success': False, 'error': '用户未登录'}, status=401)

        license_plate = data.get('license_plate')
        existing_car = Car.objects.filter(license_plate=license_plate).first()

        if not existing_car:
            return JsonResponse({'success': False, 'error': '车辆不存在'}, status=404)

        # 如果车辆已停车，且停车时间不为空，则不允许再次停车
        if existing_car.parked_at:
            return JsonResponse({'success': False, 'error': '车辆已经停车'}, status=400)
        global_settings = GlobalSettings.objects.first()
        if global_settings:
            global_settings.parking_spots -= 1
            global_settings.save()
        existing_car.parked_at = timezone.now()  # 更新停车时间
        existing_car.save()
        return JsonResponse({'success': True, 'message': '车辆已停车'}, status=200)
    else:
        return JsonResponse({'success': False, 'error': '只允许POST请求'}, status=400)
    

@login_required
@csrf_exempt
def delete_car(request):
    if request.method == 'DELETE':
        data = json.loads(request.body.decode('utf-8'))
        user = request.user
        if not user:
            return JsonResponse({'success': False, 'error': '用户未登录'}, status=401)

        license_plate = data.get('license_plate')
        car_to_remove = Car.objects.filter(license_plate=license_plate).first()

        if car_to_remove:
            if car_to_remove.parked_at:
                return JsonResponse({'success': False, 'error': '车辆还没出库'}, status=400)
            else:
                user.cars.remove(car_to_remove)
                car_to_remove.delete()
                return JsonResponse({'success': True, 'message': '车辆已删除'}, status=200)
        else:    
            return JsonResponse({'success': False, 'error': '车辆不存在'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': '只允许DELETE'}, status=400)
    

@login_required
@csrf_exempt
def reset_parking_duration(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user = request.user
        if not user:
            return JsonResponse({'success': False, 'error': '用户未登录'}, status=401)

        license_plate = data.get('license_plate')
        car_to_reset = Car.objects.filter(license_plate=license_plate).first()

        if car_to_reset:
            start_time = car_to_reset.parked_at
            end_time = timezone.now()  # 使用带有时区信息的当前时间
            parking_duration = calculate_parking_duration(start_time, end_time)
            parking_duration = round(parking_duration,2)
            parking_price = calculate_parking_price(parking_duration, car_to_reset.car_type)
            global_settings = GlobalSettings.objects.first()
            if global_settings:
                global_settings.parking_spots += 1
                global_settings.save()
            car_to_reset.parked_at = None
            car_to_reset.save()

            parking_record = ParkingRecord(car=car_to_reset, start_time=start_time, end_time=end_time, price=parking_price,license_plate=license_plate)
            parking_record.save()

            return JsonResponse({'success': True, 'message': '停车时长已重置', 'parking_duration_minutes': parking_duration,
                'parking_price': parking_price}, status=201)
        else:
            return JsonResponse({'success': False, 'error': '车辆不存在'}, status=404)
    else:
        return JsonResponse({'success': False,'error': '只允许POST请求'}, status=400)
# @login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_parking_price(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        car_type = data.get('car_type')
        new_price = float(data.get('new_price'))
        try:
            parking_rate = ParkingRate.objects.get(car_type=car_type)
            parking_rate.price_per_hour = new_price
            parking_rate.save()
            response_data = {
                'success': True,
                'message': '停车价格已更新'
            }
        except ParkingRate.DoesNotExist:
            response_data = {
                'success': False,
                'message': '车型不存在'
            }
        
        return JsonResponse(response_data)
    else:
        # 处理非POST请求的情况
        response_data = {
            'success': False,
            'message': '只允许POST请求'
        }
        return JsonResponse(response_data, status=400)
from datetime import date, datetime
from django.db.models import Sum

@csrf_exempt
def query_parking_recode_by_data(request):
    '''
    input:
        {
        "start_date": "2023-09-01",
        "end_date": "2023-09-30"
        }
    output:
    {
    "success": true,
    "data": [
        {
            "id": 1,
            "car_id": 2,
            "start_time": "2023-09-28T16:16:48.686Z",
            "end_time": "2023-09-28T16:16:51.319Z",
            "price": "6.00",
            "license_plate": "苏1234567"
        },
        {
            "id": 2,
            "car_id": 2,
            "start_time": "2023-09-28T16:16:52.559Z",
            "end_time": "2023-09-28T16:16:53.717Z",
            "price": "6.00",
            "license_plate": "苏1234567"
        }
    ],
    "number_of_records": 2,
    "total_cost": "12"}
    '''
    if request.method == 'POST':
        # 获取查询参数
        data = json.loads(request.body.decode('utf-8'))
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        # 将日期字符串转换为日期对象
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
        
        # 获取查询日期的开始时间（当天的最早时刻）
        start_datetime = datetime.combine(start_date, datetime.min.time())
        
        # 获取查询日期的结束时间（当天的最晚时刻）
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # 为查询日期的开始时间和结束时间添加时区信息
        start_datetime_with_tz = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        end_datetime_with_tz = timezone.make_aware(end_datetime, timezone.get_current_timezone())
        
        # 查询匹配日期范围的停车记录
        parking_records = ParkingRecord.objects.filter(
            start_time__range=(start_datetime_with_tz, end_datetime_with_tz),
            end_time__range=(start_datetime_with_tz, end_datetime_with_tz)
        )
        
        total_cost = parking_records.aggregate(Sum('price'))['price__sum']
        
        # 在视图中处理查询到的停车记录，例如将它们传递给模板进行渲染
        return JsonResponse({
            'success': True,
            'data': list(parking_records.values()),
            'number_of_records': parking_records.count(),
            'total_cost': total_cost
        }, safe=False)

    return JsonResponse({'success': False, 'error': '只允许POST请求'}, status=400)

@csrf_exempt
def get_parking_spots(request):
    if request.method == 'GET':
        return JsonResponse({'success': True,'number':GlobalSettings.objects.first().parking_spots,'orgin_number':GlobalSettings.objects.first().origin_parking_spots})
    return JsonResponse({'success': False, 'error': '只允许GET请求'}, status=400)