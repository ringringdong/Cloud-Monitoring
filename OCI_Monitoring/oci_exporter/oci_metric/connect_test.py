from flask import Flask, Response
import oci

app = Flask(__name__)

# OCI 클라이언트 설정
config = oci.config.from_file("~/.oci/config", "DEFAULT")
compute_client = oci.core.ComputeClient(config)

@app.route('/metrics')
def metrics():
    # 메트릭 데이터 수집
    instances = compute_client.list_instances(compartment_id=config['tenancy']).data
    metrics = []
    
    for instance in instances:
        instance_state = instance.lifecycle_state
        metrics.append(f"oci_instance_state{{instance_id=\"{instance.id}\", instance_name=\"{instance.display_name}\"}} {1 if instance_state == 'RUNNING' else 0}")
    
    # Prometheus 형식으로 응답 반환
    return Response("\n".join(metrics), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999)
