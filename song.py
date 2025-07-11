from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask import current_app as app
from markupsafe import Markup

song_bp = Blueprint("song", __name__)

def render_stars(rating):
    if not rating:
        return Markup('<span class="star-empty">☆☆☆☆☆</span>')
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    stars = '★' * full + '½' * half + '☆' * empty
    return Markup(f'<span class="star">{stars}</span>')

@song_bp.route("/")
def song_list():
    cur = app.mysql.connection.cursor()
    cur.execute("""
        SELECT s.id, s.title, a.name AS album, ar.name AS artist, a.cover_url, s.song_url,
               AVG(r.rating) AS avg_rating
        FROM songs s
        JOIN albums a ON s.album_id = a.id
        JOIN artists ar ON s.artist_id = ar.id
        LEFT JOIN ratings r ON r.song_id = s.id
        GROUP BY s.id, s.title, a.name, ar.name, a.cover_url, s.song_url
    """)
    songs = cur.fetchall()
    cur.close()
    return render_template("song_list.html", songs=songs)

@song_bp.route("/song/<int:song_id>", methods=["GET", "POST"])
def song_detail(song_id):
    cur = app.mysql.connection.cursor()
    if request.method == "POST" and "user_id" in session:
        comment_text = request.form["comment"]
        rating = request.form.get("rating")
        user_id = session["user_id"]
        # Yorum işlemleri
        # Kullanıcının bu şarkıya daha önce yorumu var mı?
        cur.execute("SELECT id FROM comments WHERE user_id = %s AND song_id = %s", (user_id, song_id))
        existing = cur.fetchone()
        if existing:
            # Güncelle
            cur.execute("UPDATE comments SET comment = %s WHERE id = %s", (comment_text, existing["id"]))
        else:
            # Yeni ekle
            cur.execute("INSERT INTO comments (user_id, song_id, comment) VALUES (%s, %s, %s)", (user_id, song_id, comment_text))
        # Rating işlemleri
        if rating:
            cur.execute("SELECT id FROM ratings WHERE user_id = %s AND song_id = %s", (user_id, song_id))
            existing_rating = cur.fetchone()
            if existing_rating:
                cur.execute("UPDATE ratings SET rating = %s WHERE id = %s", (rating, existing_rating["id"]))
            else:
                cur.execute("INSERT INTO ratings (user_id, song_id, rating) VALUES (%s, %s, %s)", (user_id, song_id, rating))
        app.mysql.connection.commit()
        cur.close()
        return redirect(url_for("song.song_detail", song_id=song_id))

    # Şarkı ve yorumları getir
    cur.execute("""
        SELECT s.id, s.title, s.artist_id, a.name AS album, ar.name AS artist, a.cover_url, ar.photo_url
        FROM songs s
        JOIN albums a ON s.album_id = a.id
        JOIN artists ar ON s.artist_id = ar.id
        WHERE s.id = %s
    """, (song_id,))
    song = cur.fetchone()

    # Kullanıcının mevcut yorumu
    user_comment = None
    if "user_id" in session:
        cur.execute("""
            SELECT * FROM comments WHERE user_id = %s AND song_id = %s
        """, (session["user_id"], song_id))
        user_comment = cur.fetchone()

    cur.execute("""
        SELECT c.*, u.username, r.rating
        FROM comments c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN ratings r ON r.user_id = c.user_id AND r.song_id = c.song_id
        WHERE c.song_id = %s
        AND c.id = (
            SELECT MAX(id) FROM comments
            WHERE song_id = %s AND user_id = c.user_id
        )
        ORDER BY c.created_at DESC
    """, (song_id, song_id))
    comments = cur.fetchall()
    cur.execute("""
        SELECT CAST(ROUND(AVG(rating),2) AS DOUBLE) as avg_rating
        FROM ratings
        WHERE song_id = %s
    """, (song_id,))
    avg_rating = cur.fetchone()["avg_rating"]
    cur.close()
    return render_template(
        "song_detail.html",
        song=song,
        comments=comments,
        avg_rating=avg_rating,
        user_comment=user_comment
    )

@song_bp.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT user_id, song_id FROM comments WHERE id = %s", (comment_id,))
    comment = cur.fetchone()
    if not comment:
        flash("Yorum bulunamadı.")
        return redirect(request.referrer or url_for("song.song_list"))
    is_admin = session.get("is_admin")
    user_id = session.get("user_id")
    if is_admin or (user_id and comment["user_id"] == user_id):
        cur.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        app.mysql.connection.commit()
        flash("Yorum silindi.")
        # Silindikten sonra şarkı detayına dön
        return redirect(url_for("song.song_detail", song_id=comment["song_id"]))
    else:
        flash("Bu yorumu silme yetkiniz yok.")
        return redirect(request.referrer or url_for("song.song_list"))

@song_bp.route("/artist/<int:artist_id>")
def artist_songs(artist_id):
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT * FROM artists WHERE id = %s", (artist_id,))
    artist = cur.fetchone()
    cur.execute("""
        SELECT s.id, s.title, a.name AS album, s.song_url
        FROM songs s
        JOIN albums a ON s.album_id = a.id
        WHERE s.artist_id = %s
    """, (artist_id,))
    songs = cur.fetchall()
    cur.close()
    return render_template("artist_songs.html", artist=artist, songs=songs)
