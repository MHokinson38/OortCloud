#########################
# Nightfall Controller 
# Performs file upload scan, which will be sent to webhook 
# server and handled asynchronously
#########################

import os 
import json 

from nightfall import Confidence, DetectionRule, Detector, LogicalOp, Nightfall 

class NightfallController: 
    WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")

    def __init__(self): 
        # Nightfall API key is automatically pulled from ENV NIGHTFALL_API_KEY
        self.nightfall = Nightfall() 