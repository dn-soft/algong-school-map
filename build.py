#!/usr/bin/env python3
"""
알공 계약학교 지도 - 빌드 스크립트

1. MongoDB API에서 학교 데이터 조회
2. coords_cache.json에 없는 신규 학교만 Kakao API로 지오코딩
3. index.html 생성

환경 변수:
- MONGO_API_KEY: MongoDB REST API 키 (필수)
- KAKAO_REST_KEY: Kakao REST API 키 (필수)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

MONGO_API_BASE = 'http://20.196.152.99:3000'
MONGO_API_KEY = os.environ.get('MONGO_API_KEY', 'Dnsoft@312')
KAKAO_REST_KEY = os.environ.get('KAKAO_REST_KEY', '')

CACHE_FILE = 'coords_cache.json'
OUTPUT_FILE = 'index.html'

# 한국 시/군 좌표 (폴백용)
CITY_COORDS = {
    "가산":{"lat":35.8314,"lng":128.7982},"간석":{"lat":37.4644,"lng":126.7257},
    "강원":{"lat":37.8228,"lng":128.1555},"거제":{"lat":34.8806,"lng":128.6211},
    "경기":{"lat":37.4138,"lng":127.5183},"경북":{"lat":36.4919,"lng":128.8889},
    "경산":{"lat":35.8251,"lng":128.7415},"경주":{"lat":35.8562,"lng":129.2247},
    "계룡":{"lat":36.2747,"lng":127.2489},"고령":{"lat":35.726,"lng":128.2633},
    "고성":{"lat":38.3806,"lng":128.4678},"고창":{"lat":35.436,"lng":126.702},
    "고흥":{"lat":34.6045,"lng":127.2849},"공주":{"lat":36.4465,"lng":127.119},
    "광양":{"lat":34.9406,"lng":127.6956},"광주":{"lat":35.1595,"lng":126.8526},
    "광명":{"lat":37.4784,"lng":126.8648},"괴산":{"lat":36.8153,"lng":127.7866},
    "구미":{"lat":36.1198,"lng":128.3445},"군산":{"lat":35.9676,"lng":126.7369},
    "군포":{"lat":37.3616,"lng":126.9352},"금산":{"lat":36.1087,"lng":127.488},
    "김제":{"lat":35.8038,"lng":126.8808},"김천":{"lat":36.1398,"lng":128.1136},
    "김포":{"lat":37.6153,"lng":126.7156},"김해":{"lat":35.2285,"lng":128.8894},
    "나주":{"lat":35.0157,"lng":126.7108},"남양주":{"lat":37.636,"lng":127.2165},
    "남원":{"lat":35.4164,"lng":127.3906},"남해":{"lat":34.8377,"lng":127.8925},
    "논산":{"lat":36.1872,"lng":127.0987},"단양":{"lat":36.9847,"lng":128.3654},
    "담양":{"lat":35.3211,"lng":126.9882},"당진":{"lat":36.8898,"lng":126.6295},
    "대구":{"lat":35.8714,"lng":128.6014},"대전":{"lat":36.3504,"lng":127.3845},
    "동두천":{"lat":37.9034,"lng":127.0606},"동해":{"lat":37.5244,"lng":129.1143},
    "목포":{"lat":34.8118,"lng":126.3922},"무주":{"lat":35.9223,"lng":127.6606},
    "문경":{"lat":36.5866,"lng":128.1866},"보령":{"lat":36.3334,"lng":126.6127},
    "보성":{"lat":34.7714,"lng":127.08},"보은":{"lat":36.4889,"lng":127.7293},
    "봉화":{"lat":36.8931,"lng":128.7326},"부산":{"lat":35.1796,"lng":129.0756},
    "부안":{"lat":35.7315,"lng":126.7337},"부여":{"lat":36.2756,"lng":126.9097},
    "부천":{"lat":37.5034,"lng":126.766},"삼척":{"lat":37.45,"lng":129.1652},
    "상주":{"lat":36.4108,"lng":128.1593},"서귀포":{"lat":33.2541,"lng":126.56},
    "서울":{"lat":37.5665,"lng":126.978},"세종":{"lat":36.48,"lng":127.261},
    "수원":{"lat":37.2636,"lng":127.0286},"순창":{"lat":35.3745,"lng":127.1375},
    "순천":{"lat":34.9506,"lng":127.4873},"신안":{"lat":34.8264,"lng":126.1084},
    "아산":{"lat":36.7899,"lng":127.0018},"안동":{"lat":36.5684,"lng":128.7296},
    "안산":{"lat":37.3219,"lng":126.8309},"양산":{"lat":35.335,"lng":129.0372},
    "양양":{"lat":38.0753,"lng":128.6188},"양주":{"lat":37.7854,"lng":127.0459},
    "양평":{"lat":37.4912,"lng":127.4876},"여주":{"lat":37.2982,"lng":127.6373},
    "연천":{"lat":38.0964,"lng":127.0748},"영광":{"lat":35.2773,"lng":126.5121},
    "영덕":{"lat":36.415,"lng":129.3655},"영동":{"lat":36.175,"lng":127.7833},
    "영양":{"lat":36.6668,"lng":129.1125},"영월":{"lat":37.1837,"lng":128.4615},
    "영주":{"lat":36.8057,"lng":128.624},"영천":{"lat":35.9733,"lng":128.9386},
    "예산":{"lat":36.6826,"lng":126.8482},"예천":{"lat":36.6575,"lng":128.4527},
    "옥천":{"lat":36.3065,"lng":127.5713},"완주":{"lat":35.9044,"lng":127.162},
    "용인":{"lat":37.2411,"lng":127.1776},"울릉":{"lat":37.4843,"lng":130.9056},
    "울산":{"lat":35.5384,"lng":129.3114},"울주":{"lat":35.5222,"lng":129.2428},
    "원주":{"lat":37.3422,"lng":127.9202},"의성":{"lat":36.3528,"lng":128.697},
    "의정부":{"lat":37.7381,"lng":127.0337},"익산":{"lat":35.9483,"lng":126.9576},
    "인제":{"lat":38.0697,"lng":128.1707},"인천":{"lat":37.4563,"lng":126.7052},
    "장성":{"lat":35.3019,"lng":126.7847},"장수":{"lat":35.6474,"lng":127.5213},
    "전주":{"lat":35.8242,"lng":127.148},"정선":{"lat":37.3808,"lng":128.661},
    "정읍":{"lat":35.5699,"lng":126.8561},"제주":{"lat":33.4996,"lng":126.5312},
    "제천":{"lat":37.1326,"lng":128.191},"증평":{"lat":36.7854,"lng":127.5815},
    "진도":{"lat":34.4868,"lng":126.2633},"진주":{"lat":35.1798,"lng":128.1076},
    "진천":{"lat":36.8553,"lng":127.4354},"창원":{"lat":35.2279,"lng":128.6811},
    "천안":{"lat":36.8151,"lng":127.1139},"철원":{"lat":38.1467,"lng":127.3133},
    "청도":{"lat":35.6472,"lng":128.734},"청양":{"lat":36.4592,"lng":126.8021},
    "청주":{"lat":36.6424,"lng":127.489},"춘천":{"lat":37.8813,"lng":127.73},
    "충남":{"lat":36.5184,"lng":126.8},"충북":{"lat":36.6357,"lng":127.4912},
    "충주":{"lat":36.991,"lng":127.926},"칠곡":{"lat":35.9954,"lng":128.4018},
    "태안":{"lat":36.7454,"lng":126.2979},"파주":{"lat":37.7599,"lng":126.7802},
    "평창":{"lat":37.3706,"lng":128.3903},"평택":{"lat":36.9921,"lng":127.0858},
    "포천":{"lat":37.8949,"lng":127.2002},"포항":{"lat":36.019,"lng":129.3435},
    "하남":{"lat":37.5393,"lng":127.2144},"하동":{"lat":35.0667,"lng":127.7514},
    "해남":{"lat":34.5735,"lng":126.5993},"홍성":{"lat":36.6009,"lng":126.66},
    "홍천":{"lat":37.697,"lng":127.8886},"화성":{"lat":37.1994,"lng":126.8312},
    "화순":{"lat":35.0644,"lng":126.9868},"횡성":{"lat":37.4884,"lng":127.9847},
    "문막":{"lat":37.3038,"lng":127.8263},"삼례":{"lat":35.9072,"lng":127.0665},
    "이리":{"lat":35.9464,"lng":126.9547},"산본":{"lat":37.3922,"lng":126.9265},
    "성주":{"lat":35.9192,"lng":128.2828},"칠보":{"lat":36.4892,"lng":127.0245},
    "서초":{"lat":37.4837,"lng":127.0324},"수유":{"lat":37.6388,"lng":127.0254},
    "부평":{"lat":37.5074,"lng":126.7219},"시지":{"lat":35.8436,"lng":128.711},
    "위례":{"lat":37.4763,"lng":127.1455},"장림":{"lat":35.0735,"lng":128.9641},
    "전남":{"lat":34.816,"lng":126.463},"전라도":{"lat":35.292,"lng":126.9767},
    "전북":{"lat":35.8203,"lng":127.1088}
}


def log(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()


def fetch_schools():
    """Fetch all contract + trial schools from MongoDB"""
    log('MongoDB에서 학교 데이터 조회 중...')

    # Contract schools
    contract_pipeline = {
        "pipeline": [
            {"$match": {
                "contractYear": {"$exists": True, "$ne": []},
                "type": {"$nin": ["무료 체험", "교사연수", "연수"]},
                "office": {"$nin": ["체험교육청", "-"]},
                "schoolCode": {"$not": {"$regex": "^(dn|tst|g[0-9]|marketing|educoo|vtp)"}}
            }},
            {"$project": {"schoolName": 1, "schoolCode": 1, "office": 1,
                          "location": 1, "type": 1, "contractYear": 1, "status": 1}}
        ]
    }

    trial_pipeline = {
        "pipeline": [
            {"$match": {
                "type": "무료 체험",
                "contractYear": {"$exists": True, "$ne": []}
            }},
            {"$project": {"schoolName": 1, "schoolCode": 1, "office": 1,
                          "location": 1, "type": 1, "contractYear": 1, "status": 1}}
        ]
    }

    def post_aggregate(pipeline):
        body = json.dumps(pipeline).encode('utf-8')
        req = urllib.request.Request(
            MONGO_API_BASE + '/databases/product/collections/schools/aggregate',
            data=body,
            headers={'x-api-key': MONGO_API_KEY, 'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())['data']

    contract_raw = post_aggregate(contract_pipeline)
    trial_raw = post_aggregate(trial_pipeline)

    def normalize(raw, typ):
        out = []
        for s in raw:
            cy = s.get('contractYear', []) or []
            latest = max(cy, key=lambda x: x.get('year', 0) or 0) if cy else {}
            out.append({
                'name': s.get('schoolName', ''),
                'code': s.get('schoolCode', ''),
                'office': s.get('office', ''),
                'location': (s.get('location') or '').strip(),
                'year': latest.get('year', 0) or 0,
                'startDate': latest.get('startDate', '') or '',
                'endDate': latest.get('endDate', '') or '',
                'students': latest.get('contractStudentNumber', 0) or 0,
                'classes': latest.get('classCount', 0) or 0,
                'active': bool(s.get('status', False)),
                'type': typ
            })
        return out

    contract = normalize(contract_raw, 'contract')
    trial = normalize(trial_raw, 'trial')

    log('  계약학교: {}, 무료체험: {}'.format(len(contract), len(trial)))
    return contract + trial


def clean_name(name):
    return re.sub(r'\([^)]*\)', '', name).strip()


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)


def cache_key(school):
    """Unique key per school: code + year (so repeated contract same school = same key, different year = different key)"""
    return '{}__{}'.format(school['code'], school['year'])


def kakao_search(query):
    """Search Kakao Local API"""
    if not KAKAO_REST_KEY:
        return None, None
    encoded = urllib.parse.quote(query)
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}&size=5'.format(encoded)
    req = urllib.request.Request(url, headers={'Authorization': 'KakaoAK ' + KAKAO_REST_KEY})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            docs = json.loads(resp.read().decode()).get('documents', [])
            # Prefer school result
            for d in docs:
                pname = d.get('place_name', '')
                if any(k in pname for k in ['초등학교', '중학교', '고등학교']):
                    return float(d['y']), float(d['x'])
            if docs:
                d = docs[0]
                return float(d['y']), float(d['x'])
    except Exception as e:
        log('  Kakao error: {}'.format(e))
    return None, None


def geocode_school(school):
    """Geocode a school using Kakao API with multiple query fallbacks"""
    name = school['name']
    loc = school['location']
    cleaned = clean_name(name)

    # Build candidates
    candidates = []
    if cleaned.endswith('초등학교') or cleaned.endswith('중학교') or cleaned.endswith('고등학교'):
        candidates.append(cleaned + ' ' + loc)
        candidates.append(cleaned)
    elif cleaned.endswith('초'):
        candidates.append(cleaned + '등학교 ' + loc)
        candidates.append(cleaned + '등학교')
    else:
        candidates.append(cleaned + '초등학교 ' + loc)
        candidates.append(cleaned + '초등학교')
        candidates.append(cleaned + ' ' + loc)

    for query in candidates:
        lat, lng = kakao_search(query)
        if lat is not None:
            return round(lat, 6), round(lng, 6)
        time.sleep(0.15)
    return None, None


def geocode_new_schools(schools, cache):
    """Geocode schools not in cache"""
    new_count = 0
    success = 0
    fail = 0

    for i, s in enumerate(schools):
        key = cache_key(s)
        if key in cache:
            # Use cached
            c = cache[key]
            if c.get('lat') is not None:
                s['lat'] = c['lat']
                s['lng'] = c['lng']
                continue
            else:
                # Previously failed, try fallback
                pass

        new_count += 1
        lat, lng = geocode_school(s)
        if lat is not None:
            s['lat'] = lat
            s['lng'] = lng
            cache[key] = {'lat': lat, 'lng': lng, 'name': s['name'], 'location': s['location']}
            success += 1
        else:
            # City fallback
            if s['location'] in CITY_COORDS:
                s['lat'] = CITY_COORDS[s['location']]['lat']
                s['lng'] = CITY_COORDS[s['location']]['lng']
            else:
                s['lat'] = 36.5
                s['lng'] = 127.8
            cache[key] = {'lat': None, 'lng': None, 'name': s['name'], 'location': s['location']}
            fail += 1
        time.sleep(0.15)

    log('  신규 지오코딩: 성공 {}, 실패(폴백) {}'.format(success, fail))
    return new_count


def apply_city_fallback_for_cached_fails(schools, cache):
    """For schools that were previously failed in cache, apply city coords"""
    for s in schools:
        if 'lat' in s:
            continue
        key = cache_key(s)
        if key in cache and cache[key].get('lat') is None:
            if s['location'] in CITY_COORDS:
                s['lat'] = CITY_COORDS[s['location']]['lat']
                s['lng'] = CITY_COORDS[s['location']]['lng']
            else:
                s['lat'] = 36.5
                s['lng'] = 127.8


def render_html(schools):
    """Generate index.html from schools data"""
    all_json = json.dumps(schools, ensure_ascii=False, separators=(',', ':'))
    offices = sorted(set(s['office'] for s in schools if s['type'] == 'contract'))
    office_options = '\n'.join(
        '    <option value="{}">{}</option>'.format(o, o.replace("교육청", ""))
        for o in offices
    )
    contract_count = sum(1 for s in schools if s['type'] == 'contract')
    trial_count = sum(1 for s in schools if s['type'] == 'trial')

    template_path = 'template.html'
    if not os.path.exists(template_path):
        log('ERROR: template.html 파일이 없습니다')
        sys.exit(1)

    with open(template_path) as f:
        html = f.read()

    html = html.replace('__ALL_SCHOOLS_JSON__', all_json)
    html = html.replace('__OFFICE_OPTIONS__', office_options)
    html = html.replace('__CONTRACT_COUNT__', str(contract_count))
    html = html.replace('__TRIAL_COUNT__', str(trial_count))
    html = html.replace('__OFFICE_COUNT__', str(len(offices)))

    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    log('  HTML 생성: {} bytes'.format(len(html)))


def main():
    log('=' * 50)
    log('알공 계약학교 지도 빌드 시작')
    log('=' * 50)

    # 1. Fetch schools
    schools = fetch_schools()

    # 2. Load cache
    cache = load_cache()
    log('캐시 로드: {}개 좌표'.format(len(cache)))

    # 3. Geocode new schools
    new_count = geocode_new_schools(schools, cache)
    log('처리 완료: 전체 {}개 중 신규 {}개 지오코딩'.format(len(schools), new_count))

    # 4. Save cache
    save_cache(cache)

    # 5. Apply city fallback for any school still without coords
    apply_city_fallback_for_cached_fails(schools, cache)

    # 6. Render HTML
    render_html(schools)

    log('빌드 완료')


if __name__ == '__main__':
    main()
