from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def science_quiz():
    return render_template('main.html', title="ScienceQuiz")

@app.route('/manage')
def manage():
    return render_template('manage.html')


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
