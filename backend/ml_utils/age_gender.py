import cv2
import numpy as np

class AgeGenderPredictor:
    def __init__(self):

        self.faceProto = "ml_models/opencv_face_detector.pbtxt"
        self.faceModel = "ml_models/opencv_face_detector_uint8.pb"
        self.genderProto = "ml_models/gender_deploy.prototxt"
        self.genderModel = "ml_models/gender_net.caffemodel"
        self.ageProto = "ml_models/age_deploy.prototxt"
        self.ageModel = "ml_models/age_net.caffemodel"
        
        self.faceNet = cv2.dnn.readNet(self.faceModel, self.faceProto)
        self.genderNet = cv2.dnn.readNet(self.genderModel, self.genderProto)
        self.ageNet = cv2.dnn.readNet(self.ageModel, self.ageProto)
        
        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.genderList = ['Male', 'Female']
        self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', 
                        '(38-43)', '(48-53)', '(60-100)']
    
    def predict(self, face_image):
        """Предсказание возраста и пола для одного лица"""

        blob = cv2.dnn.blobFromImage(
            face_image, 1.0, (227, 227), 
            self.MODEL_MEAN_VALUES, swapRB=False
        )
        
        self.genderNet.setInput(blob)
        genderPreds = self.genderNet.forward()
        gender = self.genderList[genderPreds[0].argmax()]
        
        self.ageNet.setInput(blob)
        agePreds = self.ageNet.forward()
        age = self.ageList[agePreds[0].argmax()]
        
        age_range = tuple(map(int, age.strip('()').split('-'))) if '-' in age else (0, 0)
        avg_age = sum(age_range) / 2
        
        return gender, avg_age