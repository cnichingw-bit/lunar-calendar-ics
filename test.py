#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证日历生成器功能是否正常工作
"""

import requests
import json
import sys
from datetime import datetime
from icalendar import Calendar

def test_api_connectivity():
    """测试API连接"""
    print("🔍 测试1：API连接测试")
    print("-" * 50)
    
    api_url = "https://w.yxs.bj.cn/Index/Zeri/q"
    params = {
        'mo': 'api',
        'token': '05dba5a3fc088c9781ebc24fb65a1ec6',
        'type': 'time',
        'time_yinyang': '阳历',
        'time_year': '2024',
        'time_month': '1',
        'time_day': '1',
        'time_hour': '0',
        'time_min': '0',
        'time_run': '0'
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'result' in data and data['result']:
            result = data['result']
            print("✅ API连接成功！")
            print(f"\n   获取数据示例（2024-01-01）：")
            print(f"   - 日干支：{result.get('ganzhi_day', 'N/A')}")
            print(f"   - 月干支：{result.get('ganzhi_month', 'N/A')}")
            print(f"   - 宜：{result.get('yi', 'N/A')}")
            print(f"   - 忌：{result.get('ji', 'N/A')}")
            print(f"   - 吉神：{result.get('jishen', 'N/A')}")
            print(f"   - 凶神：{result.get('xiongshen', 'N/A')}")
            return True
        else:
            print("❌ API返回数据格式错误")
            print(f"   响应：{json.dumps(data, indent=2)}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ API连接失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False


def test_ics_generation():
    """测试ICS文件生成"""
    print("\n🔍 测试2：ICS文件生成测试")
    print("-" * 50)
    
    try:
        from lunar_calendar_to_ics import LunarCalendarConverter
        from datetime import datetime, timedelta
        
        converter = LunarCalendarConverter("https://w.yxs.bj.cn/Index/Zeri/q")
        
        # 生成一个月的日历（2024年1月）
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        print(f"⏳ 生成 {start_date.date()} 到 {end_date.date()} 的日历...")
        cal = converter.create_ics_for_date_range(start_date, end_date)
        
        # 检查生成的事件数量
        events = [c for c in cal.walk('VEVENT')]
        print(f"✅ 生成成功！共生成 {len(events)} 个事件")
        
        if events:
            first_event = events[0]
            print(f"\n   第一个事件示例：")
            print(f"   - 标题：{first_event.get('summary')}")
            print(f"   - 描述：{first_event.get('description')[:50]}...")
            print(f"   - 分类：{first_event.get('categories', 'N/A')}")
        
        return True
        
    except ImportError:
        print("❌ 依赖包未安装，请运行：pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """测试依赖包"""
    print("\n🔍 测试3：依赖包检查")
    print("-" * 50)
    
    packages = ['requests', 'icalendar', 'pytz']
    all_ok = True
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package:<15} 已安装")
        except ImportError:
            print(f"❌ {package:<15} 未安装")
            all_ok = False
    
    if not all_ok:
        print("\n💡 请运行以下命令安装依赖：")
        print("   pip install -r requirements.txt")
    
    return all_ok


def test_color_category():
    """测试颜色分类逻辑"""
    print("\n🔍 测试4：颜色分类逻辑测试")
    print("-" * 50)
    
    try:
        from lunar_calendar_to_ics import LunarCalendarConverter
        
        converter = LunarCalendarConverter("https://w.yxs.bj.cn/Index/Zeri/q")
        
        test_cases = [
            {
                "name": "包含天德吉神",
                "data": {
                    "jishen": "天德、天赦",
                    "xiongshen": "",
                    "yi": "祭祀"
                },
                "expected": "RED"
            },
            {
                "name": "包含月破凶神",
                "data": {
                    "jishen": "天德",
                    "xiongshen": "月破",
                    "yi": "祭祀"
                },
                "expected": "GRAY"
            },
            {
                "name": "日值四离",
                "data": {
                    "jishen": "天德",
                    "xiongshen": "",
                    "yi": "祭祀、日值四离"
                },
                "expected": "GRAY"
            },
            {
                "name": "无特殊标记",
                "data": {
                    "jishen": "",
                    "xiongshen": "",
                    "yi": "祭祀"
                },
                "expected": "DEFAULT"
            }
        ]
        
        all_pass = True
        for test_case in test_cases:
            result = converter.determine_color_category(test_case["data"])
            status = "✅" if result == test_case["expected"] else "❌"
            print(f"{status} {test_case['name']:<15} → {result} (期望: {test_case['expected']})")
            if result != test_case["expected"]:
                all_pass = False
        
        return all_pass
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 50)
    print("🧪 农历日历ICS生成器 - 功能测试")
    print("=" * 50)
    
    tests = [
        ("依赖包", test_dependencies),
        ("API连接", test_api_connectivity),
        ("ICS生成", test_ics_generation),
        ("颜色逻辑", test_color_category),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ 测试出错：{e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总体结果：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！您可以开始使用了！")
        print("\n运行命令：python lunar_calendar_to_ics.py 2024 1 2024 12")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        return 1


if __name__ == '__main__':
    sys.exit(main())
