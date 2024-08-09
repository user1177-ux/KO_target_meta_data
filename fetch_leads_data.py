import requests
import csv
import os
import json
from datetime import datetime, timedelta

def fetch_leads_data():
    access_token = os.getenv('ACCESS_TOKEN')
    ad_account_id = os.getenv('AD_ACCOUNT_ID')

    if not access_token or not ad_account_id:
        print("ACCESS_TOKEN или AD_ACCOUNT_ID не установлены")
        return

    # Даты
    end_date = datetime.now() - timedelta(days=1)
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date = '2024-06-01'  # Начальная дата

    url = f'https://graph.facebook.com/v20.0/act_{ad_account_id}/ads'
    params = {'access_token': access_token}

    response = requests.get(url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Ошибка в ответе API: {data['error']}")
        return

    if 'data' not in data:
        print("Ответ API не содержит ключ 'data'")
        print("Полный ответ:", data)
        return

    print(f"Получено {len(data['data'])} объявлений")

    result = []
    for ad in data['data']:
        insights_url = f'https://graph.facebook.com/v20.0/{ad["id"]}/insights'
        insights_params = {
            'fields': 'ad_name,ad_id,reach,frequency,spend,actions',
            'access_token': access_token,
            'time_range': json.dumps({'since': start_date, 'until': end_date_str}),
        }
        response = requests.get(insights_url, params=insights_params)
        insights_data = response.json()

        if 'error' in insights_data:
            print(f"Ошибка в ответе API при запросе insights: {insights_data['error']}")
            continue

        if 'data' not in insights_data:
            print("Ответ API на запрос insights не содержит ключ 'data'")
            continue

        for record in insights_data['data']:
            lead_action = next((action for action in record.get('actions', []) if action['action_type'] == 'lead'), None)
            lead_value = int(lead_action['value']) if lead_action else 0
            spend = float(record['spend'])
            reach = int(record['reach'])
            frequency = float(record['frequency'])
            ad_name = record['ad_name']

            result.append({
                'Реклама': ad_name,
                'Результат': lead_value,
                'Охват': reach,
                'Частота': frequency,
                'Цена за результат': f"{spend}".replace('.', ',')
            })

    if result:
        print(f"Запись {len(result)} записей в файл")
        keys = result[0].keys()
        file_path = 'facebook_ads_leads_data.csv'
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(result)

        # Добавляем метку времени в конец файла, чтобы GitHub видел изменения
        with open(file_path, 'a') as f:
            f.write(f"\n# Last updated: {datetime.now().isoformat()}\n")

        print("Данные успешно экспортированы в", file_path)
    else:
        print("Нет данных для экспорта")

if __name__ == "__main__":
    fetch_leads_data()
