import requests

from models import AdminSetting


def open_gate():
    result = {
        'status': 'error',
        'message': 'Ошибка при вызове API',
        'code': 500,
    }
    api_key = AdminSetting.query.filter_by(key='zvonok_api_key').first()
    if not api_key:
        result['message'] = 'Не указан API ключ'
        return result
    api_key = api_key.value
    phone = AdminSetting.query.filter_by(key='gate_phone').first()
    if not phone:
        result['message'] = 'Не указан номер шлагбаума'
        return result
    phone = phone.value
    campaign_id = AdminSetting.query.filter_by(key='campaign_id').first()
    if not campaign_id:
        result['message'] = 'Не указан ID кампании'
        return result
    campaign_id = campaign_id.value
    url = f'https://zvonok.com/manager/cabapi_external/api/v1/phones/call/?public_key={api_key}&phone={phone}&campaign_id={campaign_id}'
    response = requests.get(url)
    if response.status_code == 200:
        result['status'] = 'success'
        result['message'] = 'Звонок успешно совершен'
        result['code'] = 200
    return result
