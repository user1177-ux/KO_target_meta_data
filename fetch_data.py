import requests
import csv

# Данные для доступа
access_token = '<ACCESS_TOKEN>'
ad_account_id = '<AD_ACCOUNT_ID>'

# URL для запроса данных
url = f'https://graph.facebook.com/v12.0/act_{ad_account_id}/insights'

# Параметры запроса
params = {
    'fields': 'campaign_name,campaign_id,clicks,reach,impressions,actions,cpc,spend',
    'access_token': access_token,
    'time_increment': 1
}

# Выполнение запроса
response = requests.get(url, params=params)

# Проверка на успешность запроса
if response.status_code == 200:
    data = response.json()
    if 'data' in data:
        data = data['data']
        
        with open('facebook_ads_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['Дата', 'Клики', 'Охват', 'Показы', 'Бюджет', 'Заявки', 'Кампания']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for record in data:
                lead_value = next((action['value'] for action in record['actions'] if action['action_type'] == 'lead'), 0)
                campaign = 'RU' if 'русский' in record['campaign_name'].lower() else 'EN' if 'английский' in record['campaign_name'].lower() else 'SLO'
                writer.writerow({
                    'Дата': record['date_start'],
                    'Клики': record['clicks'],
                    'Охват': record['reach'],
                    'Показы': record['impressions'],
                    'Бюджет': record['spend'],
                    'Заявки': lead_value,
                    'Кампания': campaign
                })
    else:
        print("Ошибка: ключ 'data' не найден в ответе API. Ответ:", data)
else:
    print(f"Ошибка запроса API: {response.status_code}. Ответ: {response.text}")
