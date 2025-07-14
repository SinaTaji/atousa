from kavenegar import *
from decouple import config


def send_otp(phone, code):
    try:
        api = KavenegarAPI(config('KaveNegar_ApiKey'))
        params = {'sender': '1000689696',
                  'receptor': phone,
                  'message': f'به فروشگاه بزرگ آتوسا خوش آمدید \n کد تایید شما {code}'}
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
