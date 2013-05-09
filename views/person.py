#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import operator
import time

from flask import redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc

from database import db_session
from models.person import Person


def register(app):

    person_names_json = json.dumps(all_person_names())

    # 루트
    @app.route('/person/', methods=['GET'])
    def person_main():
        query = request.args.get('q', None)

        if query is not None:
            return redirect(url_for('search', query=query))

        people = Person.query.order_by(desc(Person.id))
        return render_template('people.html', people=people)

    @app.route('/person/all-names.json', methods=['GET'])
    def person_all_names():
        return person_names_json

    # 이름으로 검색
    @app.route('/person/q/<query>', methods=['GET'])
    def search(query):
        # TODO: validation & sanitization
        # TODO: 처음엔 몇 개만 받아오고, '더 보기'를 누르면 나머지를 가져옴
        results = Person.query.filter(or_(
                    Person.name.like(u'%{0}%'.format(query)),
                    Person.name_en.ilike(u'%{0}%'.format(query))
                )).all()

        if len(results) == 1:
            person = results[0]
            return redirect(url_for('person', id=person.id))

        return render_template('search-results.html', results=results,
                query=query)

    # 사람
    @app.route('/person/<int:id>', methods=['GET'])
    def person(id):
        try:
            person = Person.query.filter_by(id=id).one()
        except NoResultFound, e:
            return render_template('not-found.html'), 404

        try:
            person_extra_vars = json.loads(person.extra_vars)
            if type(person_extra_vars.get('experience', None)) in [str, unicode]:
                person_extra_vars['experience'] = [person_extra_vars['experience']]
        except ValueError, e:
            pass

        log_person(id)
        return render_template('person.html', person=person,
                person_extra_vars=person_extra_vars)


def all_person_names():
    name_tuples = (list(i) for i in db_session.query(
        Person.name,
        Person.name_en,
        ))
    all_names = list(set(reduce(operator.add, name_tuples)))
    return all_names


def log_person(id):
    # FIXME: make this work w/ postgres
    # db['log_person'].insert({
    #     'id': id,
    #     'date': time.time()
    # })
    pass
