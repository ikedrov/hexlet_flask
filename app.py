import os
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import json
import re

app = Flask(__name__)
app.secret_key = "secret_key"
user_emails = []
usernames = []
user_ids = []


def validate(user):
    errors = {}
    if not user['username']:
        errors['username'] = "Can't be blank"
    if len(user['username']) < 4:
        errors['username'] = 'Username must be at least 4 characters'
    if not user['email']:
        errors['email'] = "Can't be blank"
    if user['email'] in user_emails:
        errors['email'] = 'User email already exists'
    if user['username'] in usernames:
        errors['username'] = 'Username already exists'
    if len(re.sub("[A-Za-z0-9]", '', user["username"])) != 0:
        errors['username'] = 'Username must consist of letters or numbers'
    if len(re.sub("[A-Za-z0-9.@-]", '', user["email"])) != 0:
        errors['email'] = 'Email must consist of letters or numbers and "@"'
    return errors


def new_id():
    try:
        with open('users.json') as f:
            data = [json.load(f)]
            last_user = data[0]['user'][-1]['id']
            last_id = last_user + 1
            return last_id
    except FileNotFoundError:
        return 1


@app.errorhandler(404)
@app.route('/users')
def user():
    try:
        with open('users.json') as file:
            users = json.load(file)
            u_list = [users]
            term = request.args.get('term')
            filtered_users = []
            user_list = u_list[0]['user']

            if term:
                for u in user_list:
                    if term in u['username']:
                        filtered_users.append(u)
            if filtered_users:
                return render_template(
                    'users/users.html',
                    filtered_users=filtered_users,
                    search=term,)
            else:
                messages = get_flashed_messages(with_categories=True)
                return render_template(
                    'users/users.html',
                    user=users["user"], messages=messages)
    except FileNotFoundError:
        return 'File is empty', 404


@app.route('/users/new')
def users_new():
    user = {'username': '',
              'email': ''}
    errors = {}
    return render_template('users/new.html', user=user,
                                        errors=errors)


@app.post('/users')
def users_post():
    users = {}
    users['user'] = []
    user = request.form.to_dict()
    user['id'] = new_id()

    if os.path.exists('users.json'):
        with open('users.json', 'r+') as f:
            data = json.load(f)
            data_list = [data]
            info = data_list[0]['user']
            for i in info:
                user_emails.append(i['email'])
                usernames.append(i['username'])
            errors = validate(user)
            if errors:
                return render_template('users/new.html',
                                user=user, errors=errors)
            data["user"].append(user)
            f.seek(0)
            json.dump(data, f)
    else:
        with open('users.json', 'a+') as f:
            users['user'].append(user)
            json.dump(users, f)
    flash('New user has been created', 'success')
    return redirect(url_for('user'), code=302)


@app.errorhandler(404)
@app.route('/users/<int:id>/update', methods = ['GET', 'POST'])
def update_user(id):
    try:
        with open('users.json', 'r+') as f:
            data = json.load(f)
            data_list = [data]
            info = data_list[0]['user']
            user = None
            errors = {}
            for i in info:
                if i['id'] == id:
                    user = i
            if request.method == 'GET':
                return render_template(
                    'users/edit.html',
                    user=user, errors=errors)

            if request.method == 'POST':
                email = request.form.get('email')
                user['email'] = email
                data['user'][id-1]['email'] = email
                errors = validate(user)
                if errors:
                    return render_template(
                        'users/edit.html',
                        errors=errors,
                        user=user)
                with open('users.json', 'w') as file:
                    json.dump(data, file)
                flash('User was updated successfully', 'success')
                return redirect(url_for('user'), code=302)
    except FileNotFoundError:
        return 'File is empty', 404


@app.errorhandler(404)
@app.route('/users/<int:id>/delete', methods = ['GET', 'POST'])
def delete_user(id):
    try:
        with open('users.json', 'r+') as f:
            data = json.load(f)
            if request.method == 'GET':
                return render_template(
                    'users/delete.html', id=id)
            if request.method == 'POST':
                try:
                    del data['user'][id - 1]
                except:
                    return 'User not found', 404
            with open('users.json', 'w') as file:
                json.dump(data, file)
            flash('User was deleted successfully', 'success')
            return redirect(url_for('user'), code=302)
    except FileNotFoundError:
        return 'File is empty', 404


if __name__ == '__main__':
    app.run(debug=True)


