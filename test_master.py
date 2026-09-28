import sys
import json
import os
sys.path.append(os.path.abspath('backend'))
from app.services.master_orchestrator import master_orchestrator

event = json.loads(sys.argv[1])
print(json.dumps(master_orchestrator.process_event(event)))
