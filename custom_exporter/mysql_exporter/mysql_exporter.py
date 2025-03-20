from prometheus_client import start_http_server, Gauge
import mysql.connector
import time

# Prometheus metric을 설정합니다.
threads_connected_gauge = Gauge('mysql_threads_connected', 'Number of threads connected to the MySQL database')
slow_queries_gauge = Gauge('mysql_slow_queries', 'Number of slow queries in the MySQL database')
innodb_buffer_pool_read_requests_gauge = Gauge('mysql_innodb_buffer_pool_read_requests', 'Number of Innodb buffer pool read requests')
innodb_buffer_pool_pages_data_gauge = Gauge('mysql_innodb_buffer_pool_pages_data', 'Number of pages in the Innodb buffer pool that are in use')
qcache_hits_gauge = Gauge('mysql_qcache_hits', 'Number of cache hits in the MySQL query cache')
qcache_lowmem_prunes_gauge = Gauge('mysql_qcache_lowmem_prunes', 'Number of query cache low-memory prunes')
innodb_data_written_gauge = Gauge('mysql_innodb_data_written', 'Number of bytes written to InnoDB data files')
innodb_data_read_gauge = Gauge('mysql_innodb_data_read', 'Number of bytes read from InnoDB data files')
queries_gauge = Gauge('mysql_queries', 'Number of queries executed in the MySQL database')
innodb_data_reads_gauge = Gauge('mysql_innodb_data_reads', 'Number of reads from InnoDB data files')
innodb_data_writes_gauge = Gauge('mysql_innodb_data_writes', 'Number of writes to InnoDB data files')


def get_db_metrics():
   
    conn = mysql.connector.connect(
        host='localhost',
        user='monitoring_user',
        password='Password1!',
        database='mysql'
    )

    cursor = conn.cursor()


    cursor.execute("SHOW STATUS LIKE 'Threads_connected';")
    result = cursor.fetchone()
    if result:
        threads_connected_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Slow_queries';")
    result = cursor.fetchone()
    if result:
        slow_queries_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_read_requests';")
    result = cursor.fetchone()
    if result:
        innodb_buffer_pool_read_requests_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_data';")
    result = cursor.fetchone()
    if result:
        innodb_buffer_pool_pages_data_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Qcache_hits';")
    result = cursor.fetchone()
    if result:
        qcache_hits_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Qcache_lowmem_prunes';")
    result = cursor.fetchone()
    if result:
        qcache_lowmem_prunes_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Innodb_data_written';")
    result = cursor.fetchone()
    if result:
        innodb_data_written_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Innodb_data_read';")
    result = cursor.fetchone()
    if result:
        innodb_data_read_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Questions';")
    result = cursor.fetchone()
    if result:
        queries_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Innodb_data_reads';")
    result = cursor.fetchone()
    if result:
        innodb_data_reads_gauge.set(result[1])

    cursor.execute("SHOW STATUS LIKE 'Innodb_data_writes';")
    result = cursor.fetchone()
    if result:
        innodb_data_writes_gauge.set(result[1])

    cursor.close()
    conn.close()


def run_exporter():
    start_http_server(8888) 
    while True:
        get_db_metrics()
        time.sleep(30)  

if __name__ == '__main__':
    run_exporter()
