#!/usr/bin/python3

"""
    create_account_with_captcha.py

    MediaWiki Action API Code Samples
    Demo of `createaccount` module: Create an account on a wiki with a special
    authentication extension installed. This example considers a case of a wiki
    where captcha is enabled through extensions like ConfirmEdit
    (https://www.mediawiki.org/wiki/Extension:ConfirmEdit)

    This demo app uses Flask (a Python web development framework).

    MIT license
"""

import requests
from flask import Flask, render_template, flash, request

S = requests.Session()
TEST_WIKI_URL = "https://test.wikipedia.org"
TEST_API_ENDPOINT = TEST_WIKI_URL + "/w/api.php"

MEDIA_WIKI_URL = "https://mediawiki.org"
MEDIA_API_ENDPOINT = MEDIA_WIKI_URL + "/w/api.php"

# App config.
DEBUG = True
APP = Flask(__name__)
APP.config.from_object(__name__)
APP.config['SECRET_KEY'] = 'enter_your_secret_key'


@APP.route("/", methods=['GET', 'POST'])
def show_form():
    """ Render form template and handle form submission request """

    form_fields = get_form_fields()
    captcha_url = TEST_WIKI_URL + form_fields['captcha']['captchaInfo']['value']
    if request.method == 'POST':
        details = {
            'name': request.form['username'],
            'password': request.form['password'],
            'confirm_password': request.form['retype'],
            'email': request.form['email'],
            'captcha_word': request.form['captcha-word'],
            'captcha_id': request.form['captcha-id']}

        create_account(details)

    register_fields = []

    for field_name in form_fields['reg_details']:
        field = {
            'name': field_name,
            'type': form_fields['reg_details'][field_name]['type'],
            'label': form_fields['reg_details'][field_name]['label']}
        register_fields.append(field)

    register_fields.append({
        'name': 'captcha-word',
        'type': 'text',
        'label': 'Enter the text you see on the image below'})
    register_fields.append({
        'name':'captcha-id',
        'type':'hidden',
        'value':form_fields['captcha']['captchaId']['value']})
        
    return render_template(
        'create_account_form.html',
        captcha=captcha_url,
        fields=register_fields)


def get_form_fields():
    """ Fetch the form fields from `authmanagerinfo` module """

    fields = {}

    field_attributes = {}

    response = S.get(
        url=TEST_API_ENDPOINT,
        params={
            'action': 'query',
            'meta': 'authmanagerinfo',
            'amirequestsfor': 'create',
            'format': 'json'})

    data = response.json()
    query = data and data['query']
    authmanagerinfo = query and query['authmanagerinfo']
    request_attribute = authmanagerinfo and authmanagerinfo['requests']

    for request_name in request_attribute:
        if request_name['account'] == 'CaptchaAuthenticationRequest':
            field_name = request_name and request_name['fields']
            for name in field_name:
                field_attributes[name] = field_name[name]

    response = S.get(
        url=MEDIA_API_ENDPOINT,
        params={
            'action': 'query',
            'meta': 'authmanagerinfo',
            'amirequestsfor': 'create',
            'format': 'json'})

    data = response.json()
    query = data and data['query']
    authmanagerinfo = query and query['authmanagerinfo']
    request_attribute = authmanagerinfo and authmanagerinfo['requests']

    fields['captcha'] = field_attributes

    field_attributes = {}

    for request_name in request_attribute:
        if (request_name['id'] == 'MediaWiki\\Auth\\PasswordAuthenticationRequest' or
                request_name['id'] == 'MediaWiki\\Auth\\UserDataAuthenticationRequest'):
            field_name = request_name and request_name['fields']
            for name in field_name:
                field_attributes[name] = field_name[name]

    fields['reg_details'] = field_attributes

    return fields


def create_account(details):
    """ Send a post request along with create account token, user information
     and return URL to the API to create an account on a wiki """

    createtoken = fetch_create_token()

    response = S.post(url=TEST_API_ENDPOINT, data={
        'action': 'createaccount',
        'createtoken': createtoken,
        'username': details['name'],
        'password': details['password'],
        'retype': details['confirm_password'],
        'email': details['email'],
        'createreturnurl': 'http://127.0.0.1:5000/',
        'captchaId': details['captcha_id'],
        'captchaWord': details['captcha_word'],
        'format': 'json'})

    data = response.json()
    createaccount = data['createaccount']

    if createaccount['status'] == "PASS":
        flash(
            'Success! An account with username ' + details['name'] + ' has been created!')
    else:
        flash(
            'Oops! Something went wrong -- ' + createaccount['messagecode'] + "." +
            createaccount['message'])


def fetch_create_token():
    """ Fetch create account token via `tokens` module """

    response = S.get(
        url=TEST_API_ENDPOINT,
        params={
            'action': 'query',
            'meta': 'tokens',
            'type': 'createaccount',
            'format': 'json'})

    data = response.json()
    return data['query']['tokens']['createaccounttoken']


if __name__ == "__main__":
    APP.run()
