#!/usr/bin/env python3
"""
reverse_bazi.py — 从四柱八字倒推出生日期时间

原理：
  四柱八字 = 年柱 + 月柱 + 日柱 + 时柱
  日柱在60天内唯一，月柱限定节气范围，年柱限定年份范围
  通过扫描候选年份逐日匹配，精确反推出出生年月日时

用法：
  # 完整四柱
  python reverse_bazi.py --year 乙酉 --month 壬午 --day 甲子 --hour 庚午

  # 仅地支（不验证时干一致性）
  python reverse_bazi.py --year 乙酉 --month 壬午 --day 甲子 --hour 午

  # 指定年份范围
  python reverse_bazi.py --year 乙酉 --month 壬午 --day 甲子 --hour 庚午 --range 2000 2050

  # JSON 输出
  python reverse_bazi.py -y 乙酉 -m 壬午 -d 甲子 -t 庚午 --json
"""

import argparse
import sys
import json

from lunar_python import Solar

TIAN_GAN = '甲乙丙丁戊己庚辛壬癸'
DI_ZHI = '子丑寅卯辰巳午未申酉戌亥'
DI_ZHI_HOUR = {'子':0,'丑':1,'寅':2,'卯':3,'辰':4,'巳':5,'午':6,'未':7,'申':8,'酉':9,'戌':10,'亥':11}
SHI_CHEN_RANGE = {
    '子': (23, 1), '丑': (1, 3), '寅': (3, 5), '卯': (5, 7),
    '辰': (7, 9), '巳': (9, 11), '午': (11, 13), '未': (13, 15),
    '申': (15, 17), '酉': (17, 19), '戌': (19, 21), '亥': (21, 23),
}


def find_candidate_years(year_gz: str, year_range: tuple) -> list:
    """找到指定年柱对应的所有公历年份（考虑立春分界）。"""
    candidates = []
    for y in range(year_range[0], year_range[1] + 1):
        try:
            s = Solar.fromYmd(y, 6, 1)
            l = s.getLunar()
            if l.getYearInGanZhiExact() == year_gz:
                candidates.append(y)
        except Exception:
            continue
    return candidates


def reverse_bazi(year_gz: str, month_gz: str, day_gz: str,
                 hour_gz: str, year_range: tuple = (1900, 2100)):
    """
    从四柱八字倒推出生日期时间。

    返回: list of dicts
      [{year, month, day, hour_dz, hour_start, hour_end, hour_verified}]
    """
    # Step 1: 找候选年份
    candidate_years = find_candidate_years(year_gz, year_range)

    # Step 2: 提取时辰
    hour_dz = hour_gz[-1]  # 时支，如 '午'
    hour_tg = hour_gz[0] if len(hour_gz) >= 2 else None
    sh, eh = SHI_CHEN_RANGE.get(hour_dz, (0, 2))

    # Step 3: 逐日扫描候选年份（含次年1月，因立春前仍有前一年柱）
    matches = []
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    for y in candidate_years:
        for cy in [y, y + 1]:
            if cy < year_range[0] or cy > year_range[1]:
                continue
            dim = list(days_in_month)
            if (cy % 4 == 0 and cy % 100 != 0) or (cy % 400 == 0):
                dim[2] = 29
            for m in range(1, 13):
                for d in range(1, dim[m] + 1):
                    try:
                        s = Solar.fromYmd(cy, m, d)
                        l = s.getLunar()
                        bz = l.getBaZi()
                        if bz[0] == year_gz and bz[1] == month_gz and bz[2] == day_gz:
                            # 验证时柱（若有完整时柱）
                            verified = True
                            if hour_tg:
                                for test_h in _get_hours_in_range(sh, eh):
                                    ts = Solar.fromYmdHms(cy, m, d, test_h, 0, 0)
                                    tl = ts.getLunar()
                                    if tl.getTimeInGanZhi() == hour_gz:
                                        verified = True
                                        break
                                    # 检查时干
                                    actual_tg = tl.getTimeGan()
                                    if actual_tg == hour_tg:
                                        verified = True
                                        break
                                else:
                                    verified = False

                            matches.append({
                                'year': cy,
                                'month': m,
                                'day': d,
                                'hour_dz': hour_dz,
                                'hour_start': sh,
                                'hour_end': eh,
                                'hour_verified': verified,
                                'display': f'{cy}年{m}月{d}日 {sh:02d}:00-{eh:02d}:00（{hour_dz}时）'
                            })
                    except Exception:
                        continue

    return matches


def _get_hours_in_range(start, end):
    """Get hour values spanning a range, handling midnight crossover."""
    if start < end:
        return list(range(start, end))
    else:
        return list(range(start, 24)) + list(range(0, end))


def main():
    parser = argparse.ArgumentParser(
        description='从四柱八字倒推出生日期时间')
    parser.add_argument('-y', '--year', required=True, help='年柱，如 乙酉')
    parser.add_argument('-m', '--month', required=True, help='月柱，如 壬午')
    parser.add_argument('-d', '--day', required=True, help='日柱，如 甲子')
    parser.add_argument('-t', '--hour', required=True, help='时柱，如 庚午 或 午（仅地支）')
    parser.add_argument('-r', '--range', nargs=2, type=int,
                        default=None, help='年份搜索范围，如 2000 2050')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    parser.add_argument('--brief', action='store_true',
                        help='简洁输出（仅第一个匹配结果）')

    args = parser.parse_args()

    # 自动推断范围
    if args.range:
        yr = tuple(args.range)
    else:
        yr = (1900, 2100)

    matches = reverse_bazi(args.year, args.month, args.day,
                           args.hour, yr)

    if args.json:
        if args.brief and matches:
            output = [matches[0]]
        else:
            output = matches
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 文本输出
    if not matches:
        print(f'❌ 未找到匹配的出生日期')
        print(f'   四柱：{args.year} {args.month} {args.day} {args.hour}')
        print(f'   搜索范围：{yr[0]}年 - {yr[1]}年')
        return

    if args.brief:
        m = matches[0]
        verif = '✓' if m['hour_verified'] else '⚠'
        print(f'{verif} {m["display"]}')
        return

    print(f'✅ 找到 {len(matches)} 个匹配的出生日期：')
    print(f'   四柱：{args.year} {args.month} {args.day} {args.hour}')
    print()
    for i, m in enumerate(matches, 1):
        verif = '✓' if m['hour_verified'] else '⚠（时干不匹配）'
        print(f'  [{i}]  {m["display"]}  时柱验证{verif}')

    if len(matches) > 1:
        print()
        print('💡 提示：多个匹配结果，请根据命主年龄/时代确定正确日期。')
        print(f'   范围每扩大60年可能新增1个匹配。')

    # 输出一键使用命令
    if matches:
        best = matches[0]
        print()
        print(f'📋 推荐用法：')
        print(f'   python3 -c "from lunar_python import Solar; '
              f's=Solar.fromYmdHms({best["year"]},{best["month"]},{best["day"]},'
              f'{best["hour_start"]},30,0); '
              f'print(\\\"Birth: \\\", s, \\\"  BaZi: \\\", s.getLunar().getEightChar())"')


if __name__ == '__main__':
    main()
