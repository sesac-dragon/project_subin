import pymysql
import pandas as pd

def read_config():
    envs = dict([l.rstrip().split('=') for l in open('.env', 'r').readlines()])

    db_config = {}
    for k, v in envs.items():
        if 'DB' not in k:   
            continue
        k = k.split('_')[1].lower()
        if k == 'port':
            v = int(v)
        db_config[k]= v
    conn = pymysql.connect(**db_config)
    return conn

# 데이터 불러오기
def load_data():
    conn = read_config()
    query = "SELECT * FROM mountain_info"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# 고도 범주화
def load_data_apex():
    conn = read_config()
    query = """
    SELECT
      CASE
        WHEN apex <= 300 THEN '0~300m'
        WHEN apex <= 600 THEN '301~600m'
        WHEN apex <= 900 THEN '601~900m'
        WHEN apex <= 1200 THEN '901~1200m'
        WHEN apex <= 1500 THEN '1201~1500m'
        ELSE '1501m 이상'
      END AS category,
      COUNT(*) AS total
    FROM mountain_info
    WHERE apex IS NOT NULL
    GROUP BY category
    ORDER BY MIN(apex)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# 고도 범주화 + 지역별
def load_data_apex2():
    conn = read_config()
    query = """
    SELECT region,
      CASE
        WHEN apex <= 300 THEN '0~300m'
        WHEN apex <= 600 THEN '301~600m'
        WHEN apex <= 900 THEN '601~900m'
        WHEN apex <= 1200 THEN '901~1200m'
        WHEN apex <= 1500 THEN '1201~1500m'
        ELSE '1501m 이상'
      END AS category,
      COUNT(*) AS total
    FROM mountain_info
    WHERE apex IS NOT NULL
    GROUP BY region, category
    ORDER BY region, MIN(apex)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# 소요시간 범주화
def load_data_runtime():
    conn = read_config()
    query = """
    SELECT
      CASE
        WHEN run_time <= 120 THEN '2시간 이하'
        WHEN run_time <= 180 THEN '2 ~ 3시간'
        WHEN run_time <= 240 THEN '3 ~ 4시간'
        WHEN run_time <= 300 THEN '4 ~ 5시간'
        WHEN run_time <= 360 THEN '5 ~ 6시간'
        ELSE '6시간 이상'
      END AS category,
      COUNT(*) AS total
    FROM mountain_info
    WHERE run_time IS NOT NULL
    GROUP BY category
    ORDER BY MIN(run_time)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df



# 소요시간 범주화 + 지역별
def load_data_runtime2():
    conn = read_config()
    query = """
    SELECT region,
      CASE
        WHEN run_time <= 120 THEN '2시간 이하'
        WHEN run_time <= 180 THEN '2 ~ 3시간'
        WHEN run_time <= 240 THEN '3 ~ 4시간'
        WHEN run_time <= 300 THEN '4 ~ 5시간'
        WHEN run_time <= 360 THEN '5 ~ 6시간'
        ELSE '6시간 이상'
      END AS category,
      COUNT(*) AS total
    FROM mountain_info
    WHERE run_time IS NOT NULL
    GROUP BY region, category
    ORDER BY region, MIN(run_time)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df