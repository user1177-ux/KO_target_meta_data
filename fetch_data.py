import requests
import csv
import os

# Получаем значения секретов из переменных окружения
access_token = os.getenv('ACCESS_TOKEN')
ad_account_id = os.getenv('AD_ACCOUNT_ID')

url = f'https://graph.facebook.com/v12.0/act_{ad_account_id}/insights'
params = {
    'fields': 'campaign_name,campaign_id,clicks,reach,impressions,actions,cpc,spend',
    'access_token': access_token,
    'time_increment': 1
}

response = requests.get(url, params=params)
data = response.json()
print("Response data:", data)  # Добавляем диагностику

if 'data' in data:
    data = data['data']
    print("Data fetched:", data)
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
    print("No data received. Check your access token and ad account ID.")
