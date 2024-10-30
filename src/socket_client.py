from flask import Flask
from flask_socketio import SocketIO
import os

# Get absolute paths for both templates and static folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

# Configure Flask app with both template and static folder paths
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
socketio = SocketIO(app) 