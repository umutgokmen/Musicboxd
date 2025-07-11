from flask import Flask
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = "gizli_anahtar"

# MySQL ayarları
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'umtmysql'
app.config['MYSQL_DB'] = 'musicboxd_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
app.mysql = mysql  

from routes.auth import auth_bp
from routes.song import song_bp
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

app.register_blueprint(auth_bp)
app.register_blueprint(song_bp)

@app.template_filter('render_stars')
def render_stars(rating):
    if not rating:
        return '☆' * 5
    full = int(round(float(rating)))
    return '★' * full + '☆' * (5 - full)

if __name__ == "__main__":
    app.run(debug=True)