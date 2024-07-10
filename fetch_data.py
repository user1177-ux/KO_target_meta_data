import requests
import csv
import os
from datetime import datetime, timedelta

def fetch_data(time_range_name, since_date, until_date):
    access_token = os.getenv('ACCESS_TOKEN')
    ad_account_id = os.getenv('AD_ACCOUNT_ID')

    url = f'https://graph.facebook.com/v20.0/act_{ad_account_id}/campaigns'
    params = {'access_token': access_token}

    response = requests.get(url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Ошибка в ответе API: {data['error']}")
        return []

    if 'data' not in data:
        print("Ответ API не содержит ключ 'data'")
        print("Полный ответ:", data)
        return []

    result = []
    for campaign in data['data']:
        insight_url = f'https://graph.facebook.com/v20.0/{campaign["id"]}/insights'
        insight_params = {
            'fields': 'campaign_name,campaign_id,clicks,reach,impressions,actions,date_start,spend',
            'access_token': access_token,
            'time_range': {'since': since_date, 'until': until_date},
            'time_increment': 1
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
            elif 'английский' в campaign_name.lower():
                language = 'EN'
            elif 'словенский' в campaign_name.lower():
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
                'Период': time_range_name
            })

    return result

def remove_duplicates(data):
    seen = set()
    result = []
    for entry in data:
        identifier = (entry['Дата'], entry['Кампания'])
        if identifier not in seen:
            seen.add(identifier)
            result.append(entry)
    return result

def main():
    # Даты
    end_date = datetime.now() - timedelta(days=1)
    end_date_str = end_date.strftime('%Y-%m-%d')
    last_3d_start_date = (end_date - timedelta(days=3)).strftime('%Y-%m-%d')
    last_year_start_date = (end_date - timedelta(days=365)).strftime('%Y-%m-%d')

    # Получение данных
    data_last_3d = fetch_data('last_3d', last_3d_start_date, end_date_str)
    data_last_year = fetch_data('last_year', last_year_start_date, end_date_str)

    # Объединение данных и удаление дубликатов
    all_data = data_last_3d + data_last_year
    all_data = remove_duplicates(all_data)

    if all_data:
        keys = all_data[0].keys()
        file_path = 'facebook_ads_data_leads.csv'
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_data)
        
        # Добавляем метку времени в конец файла, чтобы GitHub видел изменения
        with open(file_path, 'a') as f:
            f.write(f"\n# Last updated: {datetime.now().isoformat()}\n")
        
        print("Данные успешно экспортированы в", file_path)
    else:
        print("Нет данных для экспорта")

if __name__ == "__main__":
    main()
