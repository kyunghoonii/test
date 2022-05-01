from flask import Flask, render_template,request
import database_crud
import math
from flask_paginate import Pagination, get_page_parameter


app = Flask (__name__)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/concept_search/', methods=['GET','POST'])
def concept_search():
    option = request.form["option"]
    value = request.form["value"]

    db = database_crud.CRUD()
    if option == 'gender':
        query=f'''
        select person_id
             , gender
          from (
                select person_id
                      ,case gender_source_value when 'F' then 'Female'
                                                when 'M' then 'Male' end as gender
                  from person
          ) a
         where gender ilike '%{value}%'
         group by person_id
                , gender
         order by person_id
        '''
    elif option == 'race':
        query =f'''
        select person_id
             , race_source_value
          from person
         where race_source_value like '%{value}%'
         group by person_id, race_source_value
         order by person_id
        '''
    elif option == 'ethnicity':
        query = f'''
            select person_id
                 , ethnicity_source_value
              from person
             where ethnicity_source_value like '%{value}%'
             group by person_id
                    , ethnicity_source_value
             order by person_id
        '''
    elif option == 'visit':
        query = f'''
        select person_id
             , visit_concept
          from (
            select p.person_id
                 , case v.visit_concept_id when '9201' then '입원'
                                           when '9202' then '외래'
                                           when '9203' then '응급' end as visit_concept
              from person p
             inner join visit_occurrence v on p.person_id = v.person_id
        ) a
        where visit_concept like '%{value}%'
        group by person_id
               , visit_concept
        order by person_id
        ;
        '''
    elif option == 'condition':
        query = f'''
        select p.person_id
             , c.condition_source_value
          from person p
         inner join condition_occurrence c on p.person_id = c.person_id
         where c.condition_source_value like '%{value}%'
         group by p.person_id, c.condition_source_value
         order by p.person_id
        '''
    elif option == 'drug':
        query = f'''
        select p.person_id
             , d.drug_source_value
          from person p
         inner join drug_exposure d on p.person_id = d.person_id
         where d.drug_source_value like '%{value}%'
         group by p.person_id, d.drug_source_value
         order by p.person_id
        '''
    data = db.select(query)

    return render_template("concept_search.html", data=data, option=option)

@app.route('/patient/<value>/')
def patient(value):
    db = database_crud.CRUD()
    # 총 환자 수
    if value == 'count':
        query = '''
            select count(*)
              from person;
        '''
    # 성별 환자 수
    elif value == 'gender_count':
        query = '''
        select case gender_source_value when 'M' then '남성'
                                        when 'F' then '여성' end
             , count(*)
          from person
      group by gender_source_value;
        '''
    # 인종별 환자 수
    elif value == 'race_count':
        query = '''
        select race_source_value
             , count(*)
          from person
      group by race_source_value;
        '''
    # 민족별 환자수
    elif value == 'ethnicity_count':
        query = '''
        select ethnicity_source_value
             , count(*)
          from person
      group by ethnicity_source_value;
        '''
    #     사망 수
    elif value == 'death_count':
        query = '''
        select count(*)
          from person p
    inner join death d on p.person_id = d.person_id;
        '''
    #     방문 목적에 따른 방문 수
    elif value == 'visit_concept':
        query = '''
        select p.person_id
             , case v.visit_concept_id when 9201 then '입원'
                                       when 9202 then '외래'
                                       when 9203 then '응급'
                                       else '기타' end
             , count(*)
          from person p
    inner join visit_occurrence v on p.person_id = v.person_id
      group by p.person_id, v.visit_concept_id
      order by person_id;
        '''
    #     성별에 따른 방문 수
    elif value == 'gender_visit_count':
        query = '''
        select case gender_source_value when 'M' then '남성'
                                        when 'F' then '여성' end
             , count(*)
          from person p
    inner join visit_occurrence v on p.person_id = v.person_id
      group by p.gender_source_value
        '''
    #     인종에 따른 방문 수
    elif value == 'race_visit_count':
        query = '''
        select p.race_source_value
             , count(*)
          from person p
    inner join visit_occurrence v on p.person_id = v.person_id
      group by p.race_source_value;
        '''
    #     민족별 방문 수
    elif value == 'ethnicity_visit_count':
        query = '''
        select p.ethnicity_source_value
             , count(*)
          from person p
    inner join visit_occurrence v on p.person_id = v.person_id
      group by p.ethnicity_source_value;
        '''
    elif value == 'age_visit_count':
        query = '''
        select age
             , count(*)
          from (
                 select CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 rnum
                      , case when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 0 	then '0~9세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 1 	then '10~19세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 2 	then '20~29세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 3 	then '30~39세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 4 	then '40~49세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 5 	then '50~59세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 6 	then '60~69세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 7 	then '70~79세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 8 	then '80~89세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 9 	then '90~99세'
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 10 	then '100~109세' 
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 11	then '110~119세' 
                             when CAST(extract('YEAR' from current_date)-p.year_of_birth+1 AS INTEGER)/10 = 12	then '120~129세' end age
                   from person p
                  inner join visit_occurrence v on p.person_id = v.person_id
          ) a
         group by rnum,age
         order by rnum;
        '''
    data = db.select(query)
    return render_template("patient_info.html", data=data, value=value)

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)