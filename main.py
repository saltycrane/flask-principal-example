# -*- coding: utf-8 -*-

"""
Flask-Principal notes:
    - The app's login() view sends the identity_changed signal
    - The identity_changed signal runs Principal._on_identity_changed()
    - Principal._on_identity_changed() runs Principal.set_identity()
    - Principal.set_identity() runs Principal._set_thread_identity()
    - Principal._set_thread_identity() sends the identity_loaded signal
    - The identity_loaded signal runs the function decorated by
      @identity_loaded.connect or @identity_loaded_connect_via() (i.e.
      on_identity_loaded())

"""

from __future__ import with_statement

from flask import (
    Flask, request, session, redirect, url_for, render_template, flash)
from flask.ext.principal import (
    Principal, Identity, identity_changed, identity_loaded, Need, Permission,
    AnonymousIdentity)


# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERS = {
    'admin': '',
    'bill': '',
    'sally': '',
}


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# initialize flask-principal
principals = Principal(app)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    print '>' * 10, 'on_identity_loaded()'
    if identity.name == 'admin':
        identity.provides.add(Need('superuser', 'my_value'))
    elif identity.name == 'bill':
        identity.provides.add(Need('need1', 'my_value'))
    elif identity.name == 'sally':
        identity.provides.add(Need('need2', 'my_value'))


@app.route('/')
def show_entries():
    perm1 = Permission(Need('need1', 'my_value'), Need('superuser', 'my_value'))
    perm2 = Permission(Need('need2', 'my_value'), Need('superuser', 'my_value'))
    return render_template(
        'show_entries.html',
        perm1=perm1,
        perm2=perm2,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) is None:
            error = 'Invalid username'
        elif USERS.get(username) != password:
            error = 'Invalid password'
        else:
            identity_changed.send(app, identity=Identity(request.form['username']))

            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    identity_changed.send(app, identity=AnonymousIdentity())

    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
