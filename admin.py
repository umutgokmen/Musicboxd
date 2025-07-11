from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app as app

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin_panel():
    cur = app.mysql.connection.cursor()
    # Sanatçı ekleme
    if request.method == "POST" and "artist_name" in request.form:
        name = request.form["artist_name"]
        photo_url = request.form["artist_photo"]
        cur.execute("INSERT INTO artists (name, photo_url) VALUES (%s, %s)", (name, photo_url))
        app.mysql.connection.commit()
        flash("Sanatçı eklendi!")
    # Albüm ekleme
    if request.method == "POST" and "album_name" in request.form:
        name = request.form["album_name"]
        artist_id = request.form["album_artist"]
        cover_url = request.form["album_cover"]
        cur.execute("INSERT INTO albums (name, artist_id, cover_url) VALUES (%s, %s, %s)", (name, artist_id, cover_url))
        app.mysql.connection.commit()
        flash("Albüm eklendi!")
    # Şarkı ekleme
    if request.method == "POST" and "song_title" in request.form:
        title = request.form["song_title"]
        album_id = request.form["song_album"]
        artist_id = request.form["song_artist"]
        song_url = request.form["song_url"]
        cur.execute("INSERT INTO songs (title, album_id, artist_id, song_url) VALUES (%s, %s, %s, %s)", (title, album_id, artist_id, song_url))
        app.mysql.connection.commit()
        flash("Şarkı eklendi!")
    # Listeleme için sanatçı ve albümleri çek
    cur.execute("SELECT * FROM artists")
    artists = cur.fetchall()
    cur.execute("SELECT * FROM albums")
    albums = cur.fetchall()
    cur.execute("""
        SELECT s.id, s.title, ar.name AS artist
        FROM songs s
        JOIN artists ar ON s.artist_id = ar.id
    """)
    songs = cur.fetchall()
    cur.close()
    return render_template("admin_panel.html", artists=artists, albums=albums, songs=songs)

@admin_bp.route("/admin/delete_song/<int:song_id>", methods=["POST"])
def delete_song(song_id):
    cur = app.mysql.connection.cursor()
    # Önce şarkıya bağlı yorumları ve puanları sil
    cur.execute("DELETE FROM comments WHERE song_id = %s", (song_id,))
    cur.execute("DELETE FROM ratings WHERE song_id = %s", (song_id,))
    # Sonra şarkıyı sil
    cur.execute("DELETE FROM songs WHERE id = %s", (song_id,))
    app.mysql.connection.commit()
    cur.close()
    flash("Şarkı ve ilişkili yorum/puanlar silindi!")
    return redirect(url_for("admin.admin_panel"))

@admin_bp.route("/admin/edit_song/<int:song_id>", methods=["GET", "POST"])
def edit_song(song_id):
    cur = app.mysql.connection.cursor()
    if request.method == "POST":
        title = request.form["title"]
        album_id = request.form["album_id"]
        artist_id = request.form["artist_id"]
        song_url = request.form["song_url"]
        cur.execute("""
            UPDATE songs SET title=%s, album_id=%s, artist_id=%s, song_url=%s WHERE id=%s
        """, (title, album_id, artist_id, song_url, song_id))
        app.mysql.connection.commit()
        cur.close()
        flash("Şarkı güncellendi!")
        return redirect(url_for("admin.admin_panel"))
    # GET ise mevcut şarkı, albüm ve sanatçıları çek
    cur.execute("SELECT * FROM songs WHERE id=%s", (song_id,))
    song = cur.fetchone()
    cur.execute("SELECT * FROM albums")
    albums = cur.fetchall()
    cur.execute("SELECT * FROM artists")
    artists = cur.fetchall()
    # Yorumları çek
    cur.execute("""
        SELECT c.id, c.comment, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.song_id = %s
        ORDER BY c.created_at DESC
    """, (song_id,))
    comments = cur.fetchall()
    cur.close()
    return render_template("edit_song.html", song=song, albums=albums, artists=artists, comments=comments)