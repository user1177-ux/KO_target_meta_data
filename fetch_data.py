import requests
import csv
import os
from datetime import datetime, timedelta

def fetch_data():
    access_token = os.getenv('ACCESS_TOKEN')
    ad_account_id = os.getenv('AD_ACCOUNT_ID')

    # URL для запроса данных
    url = f'https://graph.facebook.com/v20.0/act_{ad_account_id}/campaigns'
    params = {'access_token': access_token}

    response = requests.get(url, params=params)
    data = response.json()

    # Проверка на наличие ошибок в ответе
    if 'error' in data:
        print(f"Ошибка в ответе API: {data['error']}")
        return

    if 'data' not in data:
        print("Ответ API не содержит ключ 'data'")
        print("Полный ответ:", data)
        return

    result = []
    today = datetime.today().strftime('%Y-%m-%d')
    seven_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')

    for campaign in data['data']:
        insight_url = f'https://graph.facebook.com/v20.0/{campaign["id"]}/insights'
        insight_params = {
            'fields': 'campaign_name,campaign_id,clicks,reach,impressions,actions,date_start,spend',
            'access_token': access_token,
            'time_range': {'since': seven_days_ago, 'until': today}
        }
        response = requests.get(insight_url, params=insight_params)
        insight_data = response.json()

        if 'error' in insight_data:
            print(f"Ошибка в ответе API при запросе insights: {insight_data['error']}")
            continue

        if 'data' not in insight_data:
            print("Ответ API на запрос insights не содержит ключ 'data'")
            print("Полный ответ:", insight_data)
            continue

        for record in insight_data['data']:
            lead_action = next((action for action in record.get('actions', []) if action['action_type'] == 'lead'), None)
            lead_value = int(lead_action['value']) if lead_action else 0
            spend = float(record['spend'])
            impressions = int(record['impressions'])
            clicks = int(record['clicks'])
            campaign_name = record['campaign_name']
            if 'русский' in campaign_name.lower():
                language = 'RU'
            elif 'английский' in campaign_name.lower():
                language = 'EN'
            elif 'словенский' in campaign_name.lower():
                language = 'SLO'
            else:
                language = 'UNKNOWN'
            
            result.append({
                'Дата': record['date_start'],
                'Клики': clicks,
                'Охват': record['reach'],
                'Показы': impressions,
                'Бюджет': f"{spend}".replace('.', ','),
                'Заявки': lead_value,
                'Кампания': language,
            })

    print("Собранные данные:", result)

    if result:
        keys = result[0].keys()
        file_path = 'facebook_ads_data.csv'
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(result)

        print("Данные успешно экспортированы в", file_path)
    else:
        print("Нет данных для экспорта")

if __name__ == "__main__":
    fetch_data()
