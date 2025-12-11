#!/usr/bin/env python3

import datetime
from lunarcalendar import Converter, Solar, Lunar, DateNotExist

def demo():
    solar = Solar(2025, 12, 10)
    print(solar)
    lunar = Converter.Solar2Lunar(solar)
    print(lunar)
    solar = Converter.Lunar2Solar(lunar)
    print(solar)
    print(solar.to_date(), type(solar.to_date()))


tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
sheng_xiao = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
jie_qi = ["立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
          "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
          "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
          "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"]
cn_week_days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
lunar_months = ["正月", "二月", "三月", "四月", "五月", "六月",
                "七月", "八月", "九月", "十月", "冬月", "腊月"]
lunar_days = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
              "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
              "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
              "卅一"]

def get_lunar_now():
    solar = datetime.date.today()
    lunar = Converter.Solar2Lunar(solar)
    year = lunar.year
    tg = tian_gan[(year - 4) % 10]
    dz = di_zhi[(year - 4) % 12]
    sx = sheng_xiao[(year - 4) % 12]
    return f"""\
{tg}{dz} {sx}年 \
{'闰' if lunar.isleap else ''}{lunar_months[lunar.month - 1]}\
{lunar_days[lunar.day - 1]}"""


if __name__ == "__main__":
    print(get_lunar_now())
