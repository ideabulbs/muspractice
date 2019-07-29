from flask import Flask, request
import subprocess
import os
import signal
import shutil
import sys

app = Flask(__name__)

PROJECTS_DIR = sys.argv[1]  #"c:\\shared\\local_sync\\tmp\\test_reaper"
if not os.path.exists(PROJECTS_DIR) or not os.path.isdir(PROJECTS_DIR):
    raise RuntimeError("Invalid projects directory: %s" % PROJECTS_DIR)
print("Using project directory: %s" % PROJECTS_DIR)

@app.route("/start", methods=['GET'])
def start_app():
    data = request.data
    project = request.args.get("project_id")
    if not project:
        return "error. No project_id given!"
    cmd = "C:\\Program Files\\REAPER (x64)\\reaper.exe %s\\%s\\%s.RPP" % (PROJECTS_DIR, project, project)
    popen = subprocess.Popen(cmd)
    if popen.pid is not None:
        return "ok"
    else:
        return "error"

@app.route("/create_project", methods=['GET'])
def create_project():
    data = request.data
    project = request.args.get("project_id")
    if not project:
       return "error. No project_id given!"

    src_dir = "%s\\template" % (PROJECTS_DIR)
    dst_dir = "%s\\%s" % (PROJECTS_DIR, project)
    shutil.copytree(src_dir, dst_dir)
    shutil.move("%s\\template.RPP" % dst_dir, "%s\\%s.RPP" % (dst_dir, project))
    return "ok"

@app.route("/project_exists", methods=['GET'])
def project_exists():
    data = request.data
    project = request.args.get("project_id")
    if not project:
       return "error. No project_id given!"
    if os.path.exists("%s\\%s\\%s.RPP" % (PROJECTS_DIR, project, project)):
        return "true"
    return "false"


@app.route("/test")
def test_app():
    return "test ok"

@app.route("/stop")
def stop_app():
    popen = subprocess.Popen('taskkill /im reaper.exe')
    popen.communicate()
    if popen.returncode != 0:
        return "error"
    else:
        return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)