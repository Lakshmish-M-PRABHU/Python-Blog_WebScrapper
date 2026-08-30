from flask import Flask, jsonify, request
from database import get_db_connection

app = Flask(__name__)


# --------------------------------
# GET ALL POSTS
# --------------------------------

@app.route("/posts", methods=["GET"])
def get_posts():

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        search = request.args.get("search")

        if search:
            query = """
                SELECT id, title, author, published_date, url, content
                FROM posts
                WHERE title ILIKE %s
                   OR content ILIKE %s
                ORDER BY published_date DESC
            """

            search_value = f"%{search}%"

            cursor.execute(
                query,
                (search_value, search_value)
            )

        else:
            query = """
                SELECT id, title, author, published_date, url, content
                FROM posts
                ORDER BY published_date DESC
            """

            cursor.execute(query)

        rows = cursor.fetchall()

        posts = []

        for row in rows:
            posts.append({
                "id": row[0],
                "title": row[1],
                "author": row[2],
                "published_date": str(row[3]) if row[3] else None,
                "url": row[4],
                "content": row[5]
            })

        return jsonify(posts)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# --------------------------------
# GET SINGLE POST
# --------------------------------

@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT id, title, author, published_date, url, content
            FROM posts
            WHERE id = %s
        """

        cursor.execute(query, (post_id,))

        row = cursor.fetchone()

        if not row:
            return jsonify({
                "error": "Post not found"
            }), 404

        post = {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "published_date": str(row[3]) if row[3] else None,
            "url": row[4],
            "content": row[5]
        }

        return jsonify(post)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# --------------------------------
# RUN SERVER
# --------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
