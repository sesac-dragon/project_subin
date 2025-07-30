import requests
from bs4 import BeautifulSoup
import json
import re


 
def mountain_crawler():
    def total_minute(time_str):
            hours = re.search(r'(\d+)\s*시간', time_str)
            minutes = re.search(r'(\d+)\s*분', time_str)
            h = int(hours.group(1)) if hours else 0
            m = int(minutes.group(1)) if minutes else 0
            return h * 60 + m
    request = requests.get('https://www.foresttrip.go.kr/pot/cc/hm/selectHndfmsmtnMngme.do?hmpgId=FRTRL&menuId=002005',
                    headers={
                        'user-agent':  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
                    })
    jsessionid = request.cookies.get('JSESSIONID')
    wmonid = request.cookies.get('WMONID')
    cookies = {
        "JSESSIONID": jsessionid,
        "WMONID": wmonid
    }
    csrf = re.search(r'_csrf=[\w\-]+', request.text).group()

    mt_area = []
    seen = set()


    for i in range(1,10):
        data = { 'fmmntArcd' : i}

        res = requests.post(f'https://www.foresttrip.go.kr/pot/cc/hm/selectMntnList.do?{csrf}',
                        headers = {
                            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                            'referer' : 'https://www.foresttrip.go.kr/pot/cc/hm/selectHndfmsmtnMngme.do?hmpgId=FRTRL&menuId=002005',
                            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'origin': 'https://www.foresttrip.go.kr',
                            'x-requested-with': 'XMLHttpRequest'
                        }, 
                            cookies = cookies, data = data)
        
        mountains = json.loads(res.text)['mntnList']['fmmntSrchList']
        
        area = {'01': '서울/경기', '02': '강원', '03': '충북',  
            '04': '충남', '05': '경북', '06': '경남',
            '07': '전북', '08': '전남', '09': '제주', '10': '울릉도'}
            

        for mountain in mountains:
            
            nums = mountain['area'].split(',')
            names = [area.get(num, num) for num in nums]
            
            for name in names:
                key = (mountain['fmmntNm'], name)
                if key not in seen:
                    seen.add(key)

                    mt_area.append({
                        '산이름' : mountain['fmmntNm'],
                        '지역' : name,
                        'number' : mountain['fmmntSeq'],
                        '위도' : mountain['xCrd'],
                        '경도' : mountain['yCrd']
                    })
                    

    mountain_info = mt_area

    for i in range(125):
        m_number = mt_area[i]['number']
        res = requests.get(f'https://www.foresttrip.go.kr/pot/cc/hm/selectHndfmsmtnMngmeDtl.do?fmmntSeq={m_number}',
                        headers = {
                                'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                                'referer' : 'https://www.foresttrip.go.kr/pot/cc/hm/selectHndfmsmtnMngme.do?hmpgId=FRTRL&menuId=002005',
                                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'origin': 'https://www.foresttrip.go.kr',
                                'x-requested-with': 'XMLHttpRequest'
                            }, 
                                cookies = cookies)
        soup = BeautifulSoup(res.text,'html.parser')

        mountain1 = soup.select('div .text-row')

        imgs = soup.select('.pt img')

        src = []
        for img in imgs:
            src.append(img.get('src'))
        

        mt_info = []
        for m in mountain1:
            
            # select label
            label = m.select_one('div .label').text

            # 아닌경우 p태그로 검색
            content = m.select_one('p').text
        
            # 산행코스만 체크해서 table tbody
            if label == '산행코스':
                time_index = 1
                courses = m.select('table tbody tr')
                for course in courses:
                    c = course.select('td')
                    
                    key = c[0].text
                    if key == '코스1':
                        key = '추천코스'
                    elif key == '코스2(하산전용)':
                        key = '기타코스1'

                    mt_info.append({
                        key : c[1].text.strip()
                    })
                    if key == '추천코스':
                        mt_info.append({
                            '소요시간' : total_minute(c[2].text)
                        })
                    else :
                        mt_info.append({
                            f'소요시간{time_index}' : total_minute(c[2].text)
                            })
                        time_index += 1
                
            elif label == '높이':
                mt_info.append({
                    label : content.split(' ')[0]
                })
            else: 
                mt_info.append({
                label : content
                })

            # 이미지
            mt_info.append({
                '이미지' : f'https://www.foresttrip.go.kr{src[0]}'
            })

        for m_info in mt_info:
            mountain_info[i].update(m_info)
            
    return mountain_info