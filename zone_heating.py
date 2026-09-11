"""
zone_heating.py
-----------------
محاكاة خوارزمية "الإدارة الذكية للمناطق" (9-Zone Selective Heating Logic).

الفكرة:
- الخزان/السطح مقسّم إلى 9 مناطق (Zone 1 -> Zone 9).
- Zone 1 هي الأقرب لمنطقة الطلب (مثلاً نقطة السحب/المضخة)، ولهذا هي أول من
  تُفعَّل عند وجود طلب، لتوفير الطاقة (لا حاجة لتسخين كل الخزان لأجل كمية صغيرة).
- إذا استمر الطلب (أو زادت الحاجة) ولم تكفِ Zone 1 لتلبيته خلال فترة زمنية
  محددة، يتم "تمرير" الإشارة تلقائياً إلى Zone 2 المجاورة لتنضم للتسخين،
  وهكذا بالتتابع حتى Zone 9 عند الحاجة القصوى فقط.
- بهذا الشكل نستهلك أقل طاقة ممكنة مقارنة بتشغيل كل المناطق التسعة دفعة واحدة.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Zone:
    id: int
    is_active: bool = False
    temperature: float = 20.0  # درجة حرارة افتراضية عند البداية (°C)
    target_temperature: float = 60.0
    heating_rate: float = 4.0  # درجة/ثانية عند التفعيل
    cooling_rate: float = 0.5  # درجة/ثانية عند الإطفاء (تبريد طبيعي)

    def step(self):
        if self.is_active and self.temperature < self.target_temperature:
            self.temperature = min(self.target_temperature,
                                    self.temperature + self.heating_rate)
        elif not self.is_active and self.temperature > 20.0:
            self.temperature = max(20.0, self.temperature - self.cooling_rate)


class NineZoneController:
    """
    المتحكم الذكي: يدير تفعيل/تعطيل 9 مناطق تسخين بمنطق تصاعدي (Cascade Logic)
    بدل تشغيل كل المناطق دفعة واحدة، لتحقيق أقصى توفير في الطاقة.
    """

    def __init__(self, num_zones: int = 9, demand_wait_ticks: int = 3):
        self.zones: List[Zone] = [Zone(id=i + 1) for i in range(num_zones)]
        self.demand_wait_ticks = demand_wait_ticks  # مدة الانتظار قبل تصعيد الطلب لمنطقة جديدة
        self._ticks_since_last_escalation = 0
        self.power_per_zone_watt = 150.0  # استهلاك كل منطقة عند التفعيل (تقديري)
        self.log: List[str] = []

    # ---------- المنطق الأساسي ----------
    def request_fuel(self, required_flow_units: float):
        """
        يستقبل طلب سحب وقود بوحدات تدفق (flow units)، ويقرر أي مناطق تُفعَّل.
        منطق مبسّط: كل منطقة نشطة وبدرجة حرارة كافية تعطي 1 وحدة تدفق تقريباً.
        """
        # القدرة الحالية = عدد المناطق المفعّلة فعلاً (كل منطقة نشطة ≈ وحدة تدفق واحدة)
        current_capacity = sum(1 for z in self.zones if z.is_active)

        if current_capacity >= required_flow_units:
            self._ticks_since_last_escalation = 0
            return  # القدرة الحالية كافية، لا حاجة لتفعيل مناطق جديدة

        # القدرة غير كافية -> فعّل Zone 1 أولاً إذا لم تكن مفعّلة
        first_inactive = next((z for z in self.zones if not z.is_active), None)
        if first_inactive is None:
            return  # كل المناطق مفعّلة أصلاً (أقصى حالة)

        self._ticks_since_last_escalation += 1

        # فعّل Zone 1 فوراً عند أول طلب
        if not self.zones[0].is_active:
            self.zones[0].is_active = True
            self.log.append(f"[تفعيل فوري] Zone 1 فُعّلت لتلبية الطلب الأولي "
                             f"(توفيراً للطاقة بدل تشغيل كل المناطق).")
            self._ticks_since_last_escalation = 0
            return

        # إن مضت فترة الانتظار المحددة ولم تكف القدرة الحالية -> صعّد لمنطقة تالية
        if self._ticks_since_last_escalation >= self.demand_wait_ticks:
            first_inactive.is_active = True
            self.log.append(f"[تصعيد الإشارة] الطلب مستمر ولم تكفِ المناطق الحالية -> "
                             f"تفعيل {first_inactive.id if False else f'Zone {first_inactive.id}'}.")
            self._ticks_since_last_escalation = 0

    def release_demand(self):
        """عند انتهاء الطلب: أطفئ المناطق تدريجياً من الأبعد للأقرب لتوفير الطاقة."""
        for z in reversed(self.zones):
            if z.is_active:
                z.is_active = False
                self.log.append(f"[إطفاء] Zone {z.id} أُطفئت بعد انتهاء الطلب.")
                break

    def tick(self):
        for z in self.zones:
            z.step()

    # ---------- مقاييس الطاقة (للمقارنة والإثبات للجنة) ----------
    def current_power_watt(self) -> float:
        return sum(self.power_per_zone_watt for z in self.zones if z.is_active)

    def all_on_power_watt(self) -> float:
        return self.power_per_zone_watt * len(self.zones)


def demo():
    print("=== محاكاة خوارزمية الإدارة الذكية لـ 9 مناطق (Selective Heating) ===\n")
    controller = NineZoneController(num_zones=9, demand_wait_ticks=3)

    scenario = (
        [1] * 8 +   # طلب بسيط (وحدة تدفق واحدة) لمدة 8 ثوانٍ -> يكفي Zone 1
        [2] * 10 +  # الطلب يزيد لوحدتين -> يفترض تصعيد إلى Zone 2
        [0] * 6     # انتهاء الطلب -> إطفاء تدريجي
    )

    for t, demand in enumerate(scenario, start=1):
        if demand > 0:
            controller.request_fuel(required_flow_units=demand)
        else:
            controller.release_demand()

        controller.tick()

        active_ids = [z.id for z in controller.zones if z.is_active]
        print(f"t={t:>2}s | الطلب={demand} | المناطق النشطة: {active_ids} "
              f"| الاستهلاك الحالي: {controller.current_power_watt():.0f}W "
              f"(بدل {controller.all_on_power_watt():.0f}W لو شغّلنا كل المناطق دفعة واحدة)")

    print("\n--- سجل القرارات (Decision Log) ---")
    for entry in controller.log:
        print(entry)

    saved_pct = (1 - controller.power_per_zone_watt * 2 / controller.all_on_power_watt()) * 100
    print(f"\n>> أقصى عدد مناطق فُعّلت في هذا السيناريو: 2 من 9 "
          f"=> توفير طاقة يقارب {saved_pct:.0f}% مقارنة بتشغيل كل المناطق دفعة واحدة.")


if __name__ == "__main__":
    demo()
