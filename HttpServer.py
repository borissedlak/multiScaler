import ast
import logging

from flask import Flask, request

import utils
from DockerClient import DockerClient
from HttpClient import HttpClient
from QrDetector import QrDetector

app = Flask(__name__)

# logger = logging.getLogger("multiscale")
# logging.getLogger('multiscale').setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

DOCKER_SOCKET = utils.get_env_param('DOCKER_SOCKET', "unix:///var/run/docker.sock")
CONTAINER_REF = utils.get_env_param("CONTAINER_REF", "Unknown")

http_client = HttpClient()
qd = QrDetector()

docker_client = DockerClient(DOCKER_SOCKET)


# @utils.print_execution_time
@app.route("/start_video", methods=['POST'])
def start_video_processing():
    qd.start_process()
    return ""


@app.route("/stop_all", methods=['POST'])
def terminate_processing():
    qd.terminate()
    return ""


@app.route("/change_config", methods=['PUT'])
def change_config():
    service_d = ast.literal_eval(request.args.get('service_description'))
    qd.change_config(service_d)

    return ""


@app.route("/change_threads", methods=['PUT'])
def change_threads():
    threads_num = int(request.args.get('thread_number'))

    # Change the number of threads of the application
    qd.change_threads(threads_num)
    # Change the number of cores available for docker
    docker_client.update_cpu(CONTAINER_REF, threads_num)

    return ""


if __name__ == '__main__':
    start_video_processing()
    app.run(host='0.0.0.0', port=8080)
