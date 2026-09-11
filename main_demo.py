"""
main_demo.py
-------------
نقطة التشغيل الموحّدة: يجمع بين
1) محاكاة حساس الوقود بالكربون النانوي (resistance_to_fuel.py)
2) خوارزمية الإدارة الذكية للمناطق التسعة (zone_heating.py)

الهدف: عرض واحد متسلسل يثبت "منطق العمل" الكامل للجنة التحكيم
(قراءة الحساس -> حساب النسبة -> قرار تفعيل المناطق بناءً على الطلب).
"""

from resistance_to_fuel import CNTFuelSensor
from zone_heating import NineZoneController


def run_full_demo():
    print("############################################################")
    print("#   محاكاة النظام الكامل: حساس CNT + إدارة 9 مناطق تسخين   #")
    print("############################################################\n")

    # 1) قراءة نسبة الوقود من حساس الكربون النانوي
    sensor = CNTFuelSensor(r_empty_ohm=1000.0, r_full_ohm=100.0, noise_std=8.0)
    true_level = 0.74
    for _ in range(10):
        fuel_pct = sensor.get_smoothed_percentage(true_level)
    print(f"1) قراءة الحساس: نسبة الوقود المتبقي = {fuel_pct:.0f}%\n")

    # 2) بناءً على مستوى الوقود، النظام يقرر عدد "مناطق" السحب المطلوبة
    #    (مثال منطقي: كل ما قلّ الوقود، يحتاج النظام سحب من مناطق أكثر لضمان الانتظام)
    if fuel_pct > 50:
        required_zones = 1
    elif fuel_pct > 20:
        required_zones = 2
    else:
        required_zones = 3

    print(f"2) القرار: عند مستوى {fuel_pct:.0f}%، النظام يحتاج تفعيل "
          f"{required_zones} منطقة/مناطق سحب لضمان انتظام تدفق الوقود.\n")

    # 3) تشغيل المتحكم الذكي لمدة كافية لإظهار التصعيد التدريجي إن لزم
    controller = NineZoneController(num_zones=9, demand_wait_ticks=3)
    print("3) محاكاة تفعيل المناطق بمرور الوقت:\n")
    for t in range(1, 15):
        controller.request_fuel(required_flow_units=required_zones)
        controller.tick()
        active_ids = [z.id for z in controller.zones if z.is_active]
        print(f"   t={t:>2}s | المناطق النشطة: {active_ids} "
              f"| الاستهلاك: {controller.current_power_watt():.0f}W")

    print("\n--- سجل قرارات المتحكم ---")
    for entry in controller.log:
        print("   " + entry)

    print("\n=== خلاصة الإثبات الفني ===")
    print(f"- الحساس حوّل قراءة المقاومة الخام إلى نسبة دقيقة ({fuel_pct:.0f}%) دون تدخل يدوي.")
    print(f"- الخوارزمية فعّلت فقط {max(z.id for z in controller.zones if z.is_active)} "
          f"من أصل 9 مناطق، بدل تشغيلها جميعاً، مما يوفر الطاقة بشكل مباشر.")


if __name__ == "__main__":
    run_full_demo()
