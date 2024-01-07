from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from cassandra.cluster import Cluster
import time
from cassandra.query import SimpleStatement
from datetime import datetime, timedelta
app = Flask(__name__)
socketio = SocketIO(app)



def get_data_from_cassandra_article(table_name):
    cluster = Cluster(["localhost"])
    session = cluster.connect("newshub")

    query = f"SELECT * FROM {table_name}"
    result = session.execute(query)

    data = [{'id' : row.id, "author" : row.author, "title" : row.title, "url" : row.url, "source": row.source, "topic": row.topic} for row in result]

    cluster.shutdown()
    return data

def get_data_from_cassandra_trending_word_count(table_name):
    cluster = Cluster(["localhost"])
    session = cluster.connect("newshub")
    # Lấy thời điểm hiện tại
    current_time = datetime.now()
    
    # Tính thời điểm 1 tiếng trở lại
    one_hour_ago = current_time - timedelta(days=1)

    # Chuyển đổi thời điểm thành định dạng ngày-giờ của Cassandra
    current_time_cassandra_format = current_time.strftime('%Y-%m-%d %H:%M:%S')
    one_hour_ago_cassandra_format = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')
    
    # Tạo câu truy vấn với điều kiện thời gian
    query = f"SELECT * FROM {table_name}"
    # Sử dụng SimpleStatement để thực hiện câu truy vấn
    # statement = SimpleStatement(query, fetch_size=10)
    result = session.execute(query)
    # Lấy dữ liệu từ kết quả truy vấn
    data = []
    for row in result:
        if one_hour_ago_cassandra_format <= row.window.strftime('%Y-%m-%d %H:%M:%S') <= current_time_cassandra_format:
            data.append({"word": row.word, "count": row.count})
    cluster.shutdown()
    return data

def get_data_from_cassandra_source_count(table_name):
    cluster = Cluster(["localhost"])
    session = cluster.connect("newshub")
    # Lấy thời điểm hiện tại
    current_time = datetime.now()
    
    # Tính thời điểm 1 tiếng trở lại
    one_hour_ago = current_time - timedelta(days=1)

    # Chuyển đổi thời điểm thành định dạng ngày-giờ của Cassandra
    current_time_cassandra_format = current_time.strftime('%Y-%m-%d %H:%M:%S')
    one_hour_ago_cassandra_format = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')
    
    # Tạo câu truy vấn với điều kiện thời gian
    query = f"SELECT * FROM {table_name}"
    # Sử dụng SimpleStatement để thực hiện câu truy vấn
    # statement = SimpleStatement(query, fetch_size=10)
    result = session.execute(query)
    # Lấy dữ liệu từ kết quả truy vấn
    data = []
    for row in result:
        if one_hour_ago_cassandra_format <= row.window.strftime('%Y-%m-%d %H:%M:%S') <= current_time_cassandra_format:
            data.append({"source": row.source, "count": row.count})
    cluster.shutdown()
    return data

def get_data_from_cassandra_total_word_count(table_name):
    cluster = Cluster(["localhost"])
    session = cluster.connect("newshub")

    query = f"SELECT * FROM {table_name}"
    result = session.execute(query)

    data = [{"word" : row.word, "count" : row.count} for row in result]
    sorted_data = sorted(data, key=lambda x: x["count"], reverse=True)

    # Take the top 5 elements
    top_5_words = sorted_data[:5]
    cluster.shutdown()
    return top_5_words

def update_data():
    while True:
        try: 
            article_data = get_data_from_cassandra_article("article")
            trending_word_count = get_data_from_cassandra_trending_word_count("trending_word_count")
            source_count_data = get_data_from_cassandra_source_count("source_count")
            top_5_words = get_data_from_cassandra_total_word_count("total_word_count")
            # Gửi dữ liệu từ 3 bảng qua SocketIO
            socketio.emit('update_data', {
                'article': article_data,
                'source_count': source_count_data,
                'trending_word_count': trending_word_count,
                'total_word_count': top_5_words,
            })

            time.sleep(5)  # Cập nhật dữ liệu mỗi 5 giây
        except Exception as e:
            print(f"Error in update_data: {e}")

@app.route('/refreshData')
def refresh_data():
    # global dataValues, categoryValues
    dataValues = []
    categoryValues = []
    trending_word_count = get_data_from_cassandra_trending_word_count("trending_word_count")
    for i in trending_word_count:
        dataValues.append(i["count"])
        categoryValues.append(i["word"])
    # print("labels now: " + str(dataValues))
    # print("data now: " + str(categoryValues))
    return jsonify(dataValues=dataValues, categoryValues=categoryValues)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.start_background_task(target=update_data)
    socketio.run(app, debug=True)
