from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import Form
from wtforms import StringField
from flask import send_file
import scrapper
import os 

app= Flask(__name__)

app.config['SECRET_KEY'] = 'our very hard to guess secretfir'
@app.route('/', methods=['GET', 'POST'])
def index():
    errormessage = "There is no such a category in Coursera"
    if request.method == 'POST':
        search = request.form['ccategory']

        ## parsing process. 
        search_foo = scrapper.scrapCourses(search)
        if(search_foo != -1):
            filename = scrapper.visitCourse(search_foo)
            return send_file(filename, as_attachment=True)

        else:
            return render_template('base.html', errormessage = errormessage)
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)
