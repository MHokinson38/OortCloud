#########################
# Nightfall Controller 
# Performs file upload scan, which will be sent to webhook 
# server and handled asynchronously
#########################
import os 

from nightfall import Confidence, DetectionRule, Detector, Nightfall 

class NightfallController: 
    WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")
    GENERAL_DETECTOR_UUID = os.getenv("NF_GENERAL_DETECTOR_UUID")

    def __init__(self): 
        # Nightfall API key is automatically pulled from ENV NIGHTFALL_API_KEY
        self.nightfall = Nightfall() 

    def scan_file(self, file_path): 
        # Create a Detector object with the General Detector UUID
        detector = Detector(uuid=self.GENERAL_DETECTOR_UUID)

        # Create a DetectionRule object with the detector and a confidence level
        # of HIGH
        detection_rule = DetectionRule(
            detector=detector, 
            min_confidence=Confidence.HIGH
        )

        # Scan the file, webhook endpoint will notify of any findings 
        id, message = self.nightfall.scan_file(file_path, webhook_url=self.WEBHOOK_ENDPOINT, detection_rules=[detection_rule])
        print(f"Nightfall scan initiated:\tID: {id}, message: {message}")
