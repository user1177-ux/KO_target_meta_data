import requests
import csv
import os
from datetime import datetime, timedelta

def fetch_data():
    access_token = os.getenv('ACCESS_TOKEN')
    ad_account_id = os.getenv('AD_ACCOUNT_ID')

    if not access_token or not ad_account_id:
        print("Access token or Ad account ID not found.")
        return

    url = f'https://graph.facebook.com/v20.0/act_{ad_account_id}/campaigns'
    params = {'access_token': access_token}

    response = requests.get(url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"API response error: {data['error']}")
        return

    if 'data' not in data:
        print("API response does not contain 'data' key")
        print("Full response:", data)
        return

    result = []
    for campaign in data['data']:
        insight_url = f'https://graph.facebook.com/v20.0/{campaign["id"]}/insights'
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        insight_params = {
            'fields': 'campaign_name,campaign_id,clicks,reach,impressions,actions,date_start,spend',
            'access_token': access_token,
            'time_range': {'since': '2022-01-01', 'until': end_date},
            'time_increment': 1
        }
        response = requests.get(insight_url, params=insight_params)
        insight_data = response.json()

        if 'error' in insight_data:
            print(f"API response error for insights: {insight_data['error']}")
            continue

        if 'data' not in insight_data:
            print("API response for insights does not contain 'data' key")
            print("Full response:", insight_data)
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
            })

    if result:
        keys = result[0].keys()
        file_path = 'facebook_ads_data_leads.csv'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(result)

        print("Data successfully exported to", file_path)
    else:
        print("No data to export")

if __name__ == "__main__":
    fetch_data()
