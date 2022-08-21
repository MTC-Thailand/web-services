import os
import base64

import pytz
import requests
from datetime import datetime
from flask import jsonify
from flask_restful import Resource

from app.api import api
from app.extensions import db
from app.api.schema import Member, License, MemberSchema

LOGIN_URL = 'https://staging-ecredential.onespace.co.th/user/api/v1/login/service'
API_URL = 'https://dev-moph-md.onespace.co.th/manage/api/v1/medical-personnel'
base_url = 'http://www.mtc.or.th/'

tz = pytz.timezone('Asia/Bangkok')


def get_access_token():
    params = {
        'service_id': os.environ.get("INET_SERVICE_ID"),
        'service_secret': os.environ.get('INET_SERVICE_SECRET')
    }
    resp = requests.post(LOGIN_URL, json=params)
    if resp.status_code == 200:
        return resp.json()['result']['jwt_token']
    else:
        return None


class MemberPIDResource(Resource):
    def get(self, pid):
        member = db.session.query(Member).filter_by(persion_id=pid).first()
        if member:
            return {'result': True}
        else:
            return {'result': False}


class MemberINETResource(Resource):
    def get(self, mem_id):
        member = db.session.query(Member).get_or_404(mem_id)
        if not member:
            return {'message': f'Member with the ID={mem_id} not found.'}
        access_token = get_access_token()
        if access_token is None:
            return {'message': 'Authorization failed.'}, 401

        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'medical_type': 'สภาเทคนิคการแพทย์',
            'given_name': member.fname,
            'family_name': member.lname,
        }
        print(params)
        resp = requests.post(API_URL + '/find', params=params, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            return resp.json()

    def post(self, mem_id):
        member = db.session.query(Member).get_or_404(mem_id)
        if member:
            license = db.session.query(License).filter(License.mem_id == member.mem_id).first()
        access_token = get_access_token()
        if access_token is None:
            return {'message': 'Authorization failed.'}, 401

        resp = requests.get(base_url + member.pic_member, stream=True)
        if resp.status_code == 200:
            img_code = base64.b64encode(resp.content)

        min_time = datetime.min.time()
        headers = {'Authorization': f'Bearer {access_token}'}
        data = \
            {
                'pic': img_code.decode(),
                'honorific_prefix_th': 'นาย',
                'given_name_th': member.fname,
                'family_name_th': member.lname,
                'given_name_en': member.e_fname,
                'family_name_en': member.e_lname,
                'medical_license_info': {
                    'number': str(license.lic_id),
                    'type': 'สภาเทคนิคการแพทย์',
                    'approved_date': tz.localize(datetime.combine(license.appr_date, min_time)).isoformat(),
                    'license_info': {
                        'start_date': tz.localize(datetime.combine(license.lic_b_date, min_time)).isoformat(),
                        'end_date': tz.localize(datetime.combine(license.lic_exp_date, min_time)).isoformat(),
                        'license_number': str(license.lic_id),
                    }
                }
            }
        print(data)
        resp = requests.post(API_URL + '/create', json=data, headers=headers)
        return jsonify(resp.json())


class MemberResource(Resource):
    def get(self, mem_id):
        base_url = 'http://www.mtc.or.th/'
        member = db.session.query(Member).get_or_404(mem_id)
        if member:
            license = db.session.query(License).filter(License.mem_id == member.mem_id).first()
        resp = requests.get(base_url + member.pic_member, stream=True)
        if resp.status_code == 200:
            img_code = base64.b64encode(resp.content)
        min_time = datetime.min.time()

        return {'data': [
            {
                'honorific_prefix_th': member.title_id,
                'honorific_prefix_en': member.e_title,
                'pic': img_code.decode(),
                'given_name_th': member.fname,
                'family_name_th': member.lname,
                'given_name_en': member.e_fname,
                'family_name_en': member.e_lname,
                'medical_license_info': {
                    'number': str(license.lic_id),
                    'type': 'สภาเทคนิคการแพทย์',
                    'approved_date': tz.localize(datetime.combine(license.appr_date, min_time)).isoformat(),
                    'license_info': {
                        'start_date': tz.localize(datetime.combine(license.lic_b_date, min_time)).isoformat(),
                        'end_date': tz.localize(datetime.combine(license.lic_exp_date, min_time)).isoformat(),
                        'license_number': str(license.lic_id),
                    }
                }
            }
        ]}