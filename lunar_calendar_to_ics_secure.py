#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农历/阴阳历 → macOS日历ICS订阅源转换器（安全版）
功能：
- 从API获取每天的干支、宜忌、吉凶神数据
- 转换为标准ICS格式
- 使用环境变量安全保存API凭证
"""

import requests
import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz
import hashlib
from typing import Dict, List, Tuple
import sys
import os
import time
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class LunarCalendarConverter:
    def __init__(self, api_base_url: str = None):
        # 从环境变量读取配置（更安全！）
        self.api_base_url = api_base_url or os.getenv(
            'API_URL',
            'https://w.yxs.bj.cn/Index/Zeri/q'
        )
        self.api_token = os.getenv(
            'API_TOKEN',
            '05dba5a3fc088c9781ebc24fb65a1ec6'  # 默认值
        )
        
        self.timezone = pytz.timezone('Asia/Shanghai')
        
        # 吉神列表
        self.auspicious_gods = ['天德', '天德合', '月德', '月德合', '岁德', '岁德合']
        
        # 凶神标志
        self.inauspicious_keywords = ['月破', '日值四离', '日值四绝']
        
        # 请求重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 秒
    
    def fetch_daily_data(self, year: int, month: int, day: int) -> Dict:
        """
        从API获取特定日期的数据（带重试和延迟）
        
        参数：
            year: 年份
            month: 月份
            day: 日期
        
        返回：
            JSON数据字典
        """
        params = {
            'mo': 'api',
            'token': self.api_token,  # ✅ 从环境变量读取
            'type': 'time',
            'time_yinyang': '阳历',
            'time_year': str(year),
            'time_month': str(month),
            'time_day': str(day),
            'time_hour': '0',
            'time_min': '0',
            'time_run': '0'
        }
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.api_base_url,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                # 成功后添加延迟，避免过快调用
                time.sleep(0.5)
                return data
                
            except requests.Timeout:
                print(f"⏱️ 超时（尝试{attempt + 1}/{self.max_retries}）")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return None
                    
            except requests.RequestException as e:
                print(f"❌ 请求失败（尝试{attempt + 1}/{self.max_retries}）：{e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return None
        
        return None
    
    def determine_color_category(self, data: Dict) -> str:
        """
        根据吉凶神确定颜色分类
        
        规则：
        - 如果有天德相关吉神 → RED（红色）
        - 如果有月破或日值四离/四绝 → GRAY（灰色），且优先于红色
        
        返回：
            'RED' / 'GRAY' / 'DEFAULT'
        """
        has_auspicious = False
        has_inauspicious = False
        
        # 检查吉神
        jishen = data.get('jishen', '')
        if jishen:
            for god in self.auspicious_gods:
                if god in jishen:
                    has_auspicious = True
                    break
        
        # 检查凶神
        xiongshen = data.get('xiongshen', '')
        if xiongshen:
            for keyword in self.inauspicious_keywords:
                if keyword in xiongshen:
                    has_inauspicious = True
                    break
        
        # 检查宜中的禁忌
        yi = data.get('yi', '')
        if yi:
            for keyword in ['日值四离', '日值四绝']:
                if keyword in yi:
                    has_inauspicious = True
                    break
        
        # 优先级：凶神灰色 > 吉神红色
        if has_inauspicious:
            return 'GRAY'
        elif has_auspicious:
            return 'RED'
        else:
            return 'DEFAULT'
    
    def format_event_description(self, data: Dict) -> str:
        """
        格式化事件描述（宜、忌等信息）
        """
        description_parts = []
        
        # 干支信息
        ganzhi_month = data.get('ganzhi_month', '')
        if ganzhi_month:
            description_parts.append(f"【月干支】{ganzhi_month}")
        
        # 宜
        yi = data.get('yi', '')
        if yi:
            description_parts.append(f"【宜】{yi}")
        
        # 忌
        ji = data.get('ji', '')
        if ji:
            description_parts.append(f"【忌】{ji}")
        
        # 吉神
        jishen = data.get('jishen', '')
        if jishen:
            description_parts.append(f"【吉神】{jishen}")
        
        # 凶神
        xiongshen = data.get('xiongshen', '')
        if xiongshen:
            description_parts.append(f"【凶神】{xiongshen}")
        
        return '\n'.join(description_parts)
    
    def create_ics_for_date_range(self, start_date: datetime, end_date: datetime) -> Calendar:
        """
        为日期范围内的每一天创建日历事件
        
        参数：
            start_date: 开始日期
            end_date: 结束日期
        
        返回：
            icalendar.Calendar 对象
        """
        cal = Calendar()
        cal.add('prodid', '-//Lunar Calendar ICS//ZH_CN//')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', '阴阳历择日')
        cal.add('x-wr-timezone', 'Asia/Shanghai')
        cal.add('x-wr-caldesc', '每日干支、宜忌、吉凶神择日日历')
        cal.add('refresh-interval;value=duration', 'PT24H')  # 24小时刷新
        
        current_date = start_date
        event_count = 0
        error_count = 0
        
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            print(f"⏳ 处理 {year}-{month:02d}-{day:02d}...", end=' ')
            
            # 获取数据
            data = self.fetch_daily_data(year, month, day)
            
            if data and 'result' in data and data['result']:
                result = data['result']
                
                # 获取干支（日）
                ganzhi_day = result.get('ganzhi_day', '')
                
                # 创建事件
                event = Event()
                
                # 事件标题：包含日期和日干支
                event_title = f"{current_date.strftime('%m/%d')} {ganzhi_day}"
                event.add('summary', event_title)
                
                # 事件描述：包含宜、忌等详细信息
                description = self.format_event_description(result)
                event.add('description', description)
                
                # 设置日期（全天事件，DTEND 为次日，符合 RFC 5545 标准）
                event.add('dtstart', current_date.date())
                event.add('dtend', (current_date + timedelta(days=1)).date())

                # DTSTAMP 为必填字段（RFC 5545）
                event.add('dtstamp', datetime.now(self.timezone))

                # 生成唯一的UID
                uid = f"{current_date.isoformat()}-lunar-calendar@yxs.bj.cn"
                event.add('uid', uid)
                
                # 添加分类（颜色标记）
                color_category = self.determine_color_category(result)
                if color_category == 'RED':
                    event.add('categories', 'Auspicious')
                    event.add('color', 'red')
                elif color_category == 'GRAY':
                    event.add('categories', 'Inauspicious')
                    event.add('color', 'gray')
                
                # 添加创建和修改时间戳
                now = datetime.now(self.timezone)
                event.add('created', now)
                event.add('last-modified', now)
                
                # 添加事件到日历
                cal.add_component(event)
                event_count += 1
                
                print(f"✓ ({ganzhi_day})")
            else:
                error_count += 1
                print(f"✗ 数据获取失败")
            
            # 移动到下一天
            current_date += timedelta(days=1)
        
        print(f"\n📊 总计：成功{event_count}个，失败{error_count}个")
        return cal
    
    def save_ics_file(self, cal: Calendar, filepath: str):
        """
        保存ICS日历文件
        """
        try:
            with open(filepath, 'wb') as f:
                f.write(cal.to_ical())
            print(f"✅ ICS文件已保存：{filepath}")
            return True
        except Exception as e:
            print(f"❌ 保存失败：{e}")
            return False


def main():
    """
    主函数：生成日历ICS文件
    
    使用方法：
        python lunar_calendar_to_ics.py 2024 1 2025 12
        # 生成2024年1月到2025年12月的日历
    
    环境变量：
        API_TOKEN: API令牌（可选，默认使用硬编码值）
        API_URL: API地址（可选，默认使用w.yxs.bj.cn）
    """
    
    print("🌙 农历日历 ICS 生成器（安全版）")
    print("=" * 50)
    
    # 检查环境变量
    api_token = os.getenv('API_TOKEN')
    api_url = os.getenv('API_URL')
    
    if api_token:
        print(f"✅ 使用环境变量中的API_TOKEN")
    else:
        print(f"⚠️ 使用默认的API_TOKEN（建议设置环境变量以提高安全性）")
    
    if api_url:
        print(f"✅ 使用环境变量中的API_URL")
    else:
        print(f"✅ 使用默认的API_URL")
    
    print()
    
    if len(sys.argv) < 5:
        print("使用方法：python lunar_calendar_to_ics.py <start_year> <start_month> <end_year> <end_month>")
        print("示例：python lunar_calendar_to_ics.py 2024 1 2024 12")
        sys.exit(1)
    
    try:
        start_year = int(sys.argv[1])
        start_month = int(sys.argv[2])
        end_year = int(sys.argv[3])
        end_month = int(sys.argv[4])
    except ValueError:
        print("❌ 参数格式错误，请输入整数")
        sys.exit(1)
    
    # 创建转换器
    converter = LunarCalendarConverter()
    
    # 设置日期范围
    start_date = datetime(start_year, start_month, 1)
    
    # 计算结束日期（该月的最后一天）
    if end_month == 12:
        end_date = datetime(end_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(end_year, end_month + 1, 1) - timedelta(days=1)
    
    print(f"🗓️  开始生成日历：{start_date.date()} → {end_date.date()}")
    print(f"📅 总天数：{(end_date - start_date).days + 1}天\n")
    
    # 生成ICS日历
    cal = converter.create_ics_for_date_range(start_date, end_date)
    
    # 保存文件
    output_filename = f"lunar_calendar_{start_year}{start_month:02d}_to_{end_year}{end_month:02d}.ics"
    converter.save_ics_file(cal, output_filename)
    
    print(f"\n✨ 完成！您可以将 {output_filename} 上传到服务器或分享给用户")


if __name__ == '__main__':
    main()
