"""
resistance_to_fuel.py
----------------------
محاكاة "منطق العمل" (Business Logic) لحساس الوقود المصنوع من الكربون النانوي (CNT).

الفكرة الفيزيائية المبسطة:
- شريط / طبقة الكربون النانوي مغمورة جزئياً في الوقود داخل الخزان.
- كلما زاد مستوى الوقود (زاد الغمر)، قلّت مقاومة الشريط الكهربائية (لأن تلامس
  الوقود بمادة CNT الموصلة يحسّن مسار التوصيل الكهربائي عبر الشبكة النانوية).
- كلما نقص الوقود، قلّ الغمر، وارتفعت المقاومة.

هذا الملف يحوّل قراءة المقاومة الخام (بالأوم) إلى نسبة وقود متبقية (0% - 100%)
باستخدام معايرة بنقطتين (خزان فاضي / خزان معبّى) + فلترة للتشويش (noise) لمحاكاة
واقعية قراءة حساس حقيقي.
"""

import random
import statistics


class CNTFuelSensor:
    """
    يمثل حساس الكربون النانوي مع معايرة ثابتة لكل خزان.

    R_EMPTY : مقاومة الشريط عندما الخزان فاضي تماماً (أعلى مقاومة)
    R_FULL  : مقاومة الشريط عندما الخزان معبّى تماماً (أقل مقاومة)
    """

    def __init__(self, r_empty_ohm: float = 1000.0, r_full_ohm: float = 100.0,
                 noise_std: float = 8.0):
        if r_empty_ohm <= r_full_ohm:
            raise ValueError("R_EMPTY يجب أن تكون أكبر من R_FULL في هذا التصميم")
        self.r_empty = r_empty_ohm
        self.r_full = r_full_ohm
        self.noise_std = noise_std  # انحراف معياري للتشويش الكهربائي (أوم)
        self._history = []  # لتخزين آخر القراءات لعمل فلترة (smoothing)

    # ---------- الجزء الأول: محاكاة القراءة الخام من الحساس ----------
    def read_raw_resistance(self, true_fuel_fraction: float) -> float:
        """
        يحاكي قراءة المقاومة الخام القادمة من ADC متصل بشريط CNT، بافتراض
        نسبة وقود حقيقية (true_fuel_fraction بين 0 و 1)، مع إضافة تشويش عشوائي
        يمثل الاهتزاز الميكانيكي وحرارة المحيط.
        """
        true_fuel_fraction = max(0.0, min(1.0, true_fuel_fraction))
        # علاقة خطية بين المقاومة ونسبة الوقود (يمكن استبدالها بمعادلة غير خطية
        # إذا أثبتت التجارب المعملية استجابة لوغاريتمية لشبكة CNT)
        ideal_resistance = self.r_empty - (self.r_empty - self.r_full) * true_fuel_fraction
        noisy_resistance = random.gauss(ideal_resistance, self.noise_std)
        return max(self.r_full * 0.5, noisy_resistance)  # حماية من قيم سالبة غير منطقية

    # ---------- الجزء الثاني: تحويل المقاومة إلى نسبة وقود ----------
    def resistance_to_percentage(self, resistance_ohm: float) -> float:
        """
        يحوّل قراءة مقاومة (بعد الفلترة) إلى نسبة وقود 0-100%.
        """
        fraction = (self.r_empty - resistance_ohm) / (self.r_empty - self.r_full)
        fraction = max(0.0, min(1.0, fraction))
        return round(fraction * 100, 1)

    # ---------- الجزء الثالث: فلترة القراءات (Moving Average) ----------
    def get_smoothed_percentage(self, true_fuel_fraction: float, window: int = 5) -> float:
        """
        يأخذ قراءة خام جديدة، يضيفها لسجل القراءات، ثم يحسب متوسط آخر (window)
        قراءات لتفادي تذبذب القيمة النهائية المعروضة على لوحة العدادات.
        """
        raw = self.read_raw_resistance(true_fuel_fraction)
        self._history.append(raw)
        if len(self._history) > window:
            self._history.pop(0)

        smoothed_resistance = statistics.mean(self._history)
        return self.resistance_to_percentage(smoothed_resistance)


def demo():
    print("=== محاكاة حساس الوقود بالكربون النانوي (CNT Fuel Sensor) ===\n")
    sensor = CNTFuelSensor(r_empty_ohm=1000.0, r_full_ohm=100.0, noise_std=8.0)

    # مثال: الوقود الحقيقي في الخزان = 74%
    true_level = 0.74

    print(f"[محاكاة] نسبة الوقود الحقيقية المفترضة داخل الخزان: {true_level*100:.0f}%\n")
    print(f"{'#':<4}{'المقاومة الخام (Ω)':<22}{'النسبة بعد الفلترة':<20}")

    for i in range(1, 11):
        smoothed_pct = sensor.get_smoothed_percentage(true_level)
        last_raw = sensor._history[-1]
        print(f"{i:<4}{last_raw:<22.2f}{smoothed_pct:<20.1f}")

    print(f"\n>> النتيجة النهائية المعروضة على الشاشة: {smoothed_pct:.0f}% وقود متبقي")


if __name__ == "__main__":
    demo()
