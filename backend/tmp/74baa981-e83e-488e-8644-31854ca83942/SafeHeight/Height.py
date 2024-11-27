# import cv2
# import numpy as np
# from ultralytics import YOLO
# import time

# def main():
#     model = YOLO('yolov8n.pt')
#     cap = cv2.VideoCapture(0)
#     frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     safety_line_y = int(frame_height * 0.4)
#     warning_active = False
#     warning_start_time = 0
#     warning_duration = 3
    
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             break
            
#         cv2.line(frame, (0, safety_line_y), (frame_width, safety_line_y), (0, 255, 0), 2)
#         results = model(frame, classes=[0])
#         violation_detected = False
        
#         if len(results) > 0:
#             boxes = results[0].boxes
#             for box in boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 person_top = y1
                
#                 if person_top < safety_line_y:
#                     violation_detected = True
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
#                 else:
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
#         current_time = time.time()
#         if violation_detected:
#             if not warning_active:
#                 warning_active = True
#                 warning_start_time = current_time
            
#             cv2.putText(frame, "WARNING: Height Safety Violation!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
#         elif warning_active and (current_time - warning_start_time) > warning_duration:
#             warning_active = False
        
#         cv2.putText(frame, "Safety Height Limit", (10, safety_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#         cv2.imshow('Height Safety Detection', frame)
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()



import cv2
import numpy as np
from ultralytics import YOLO
import time
import datetime
import json
from pathlib import Path

class SafetyDetectionSystem:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.cap = cv2.VideoCapture(0)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.safety_zones = [
            {"y": int(self.frame_height * 0.4), "name": "Primary Zone", "color": (0, 255, 0)},
            {"y": int(self.frame_height * 0.3), "name": "Critical Zone", "color": (0, 0, 255)}
        ]
        
        self.record_path = Path("violations")
        self.record_path.mkdir(exist_ok=True)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = None
        self.recording = False
        
        self.analytics = {
            "total_violations": 0,
            "violation_durations": [],
            "peak_hours": {},
            "zones_triggered": {}
        }
        
        self.warning_active = False
        self.warning_start_time = 0
        self.warning_duration = 3
        self.detection_confidence = 0.5
        self.enable_recording = True
    
    def start_recording(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = str(self.record_path / f"violation_{timestamp}.avi")
        self.out = cv2.VideoWriter(video_path, self.fourcc, 20.0, 
                                 (self.frame_width, self.frame_height))
        self.recording = True
        
    def stop_recording(self):
        if self.recording:
            self.out.release()
            self.recording = False
    
    def log_violation(self, zone_name):
        timestamp = datetime.datetime.now()
        hour = timestamp.strftime("%H:00")
        
        self.analytics["total_violations"] += 1
        self.analytics["peak_hours"][hour] = self.analytics["peak_hours"].get(hour, 0) + 1
        self.analytics["zones_triggered"][zone_name] = self.analytics["zones_triggered"].get(zone_name, 0) + 1
        
        with open("violations.json", "w") as f:
            json.dump(self.analytics, f, indent=4)
    
    def draw_analytics(self, frame):
        info_text = [
            f"Total Violations: {self.analytics['total_violations']}",
            f"Current Time: {datetime.datetime.now().strftime('%H:%M:%S')}",
            f"Detection Confidence: {self.detection_confidence:.2f}"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, self.frame_height - 30 - (i * 30)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def process_frame(self, frame):
        violation_detected = False
        violated_zones = []
        
        for zone in self.safety_zones:
            cv2.line(frame, (0, zone["y"]), (self.frame_width, zone["y"]), 
                    zone["color"], 2)
            cv2.putText(frame, zone["name"], (10, zone["y"] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, zone["color"], 2)
        
        results = self.model(frame, classes=[0], conf=self.detection_confidence)
        
        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                person_top = y1
                confidence = float(box.conf[0])
                
                for zone in self.safety_zones:
                    if person_top < zone["y"]:
                        violation_detected = True
                        violated_zones.append(zone["name"])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        break
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                cv2.putText(frame, f"{confidence:.2f}", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame, violation_detected, violated_zones
    
    def run(self):
        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    break
                
                frame, violation_detected, violated_zones = self.process_frame(frame)
                current_time = time.time()
                
                if violation_detected:
                    if not self.warning_active:
                        self.warning_active = True
                        self.warning_start_time = current_time
                        
                        if self.enable_recording and not self.recording:
                            self.start_recording()
                        
                        for zone in violated_zones:
                            self.log_violation(zone)
                    
                    warning_text = "WARNING: Safety Violation in " + ", ".join(violated_zones)
                    cv2.putText(frame, warning_text, (50, 50),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if self.recording:
                        self.out.write(frame)
                
                elif self.warning_active and (current_time - self.warning_start_time) > self.warning_duration:
                    self.warning_active = False
                    if self.recording:
                        self.stop_recording()
                
                self.draw_analytics(frame)
                cv2.imshow('Enhanced Safety Detection', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.enable_recording = not self.enable_recording
                elif key == ord('+'):
                    self.detection_confidence = min(0.95, self.detection_confidence + 0.05)
                elif key == ord('-'):
                    self.detection_confidence = max(0.05, self.detection_confidence - 0.05)
                    
        finally:
            self.cap.release()
            self.stop_recording()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    system = SafetyDetectionSystem()
    system.run()