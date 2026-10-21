import pickle
import tensorflow as tf
import cv2
import numpy as np
import sys
import json


def write_file(dictionaries, filename):
	with open(filename, 'w+') as json_file:
		data = dictionaries
		jsoned_data = json.dumps(data, indent=True)
		json_file.write(jsoned_data)


video = sys.argv[1]
with open("label_encoder.pkl", "rb") as f:
		le = pickle.load(f)
		f.close()
with open("onehot_encoder.pkl", "rb") as f:
    ohe = pickle.load(f)
    f.close()
model = tf.keras.models.load_model("effects_model")
cap = cv2.VideoCapture("./static/saved_videos/"+video)

json_list = list()

framecount = 0
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (224,224))
        frame = frame/255.0
        results = model.predict(np.array([frame]))
        results_ohe = ohe.inverse_transform(results)
        pred = le.inverse_transform(results_ohe.ravel())[0]

        dictionary = {
            f"frame_{framecount}":{
                "effect": pred
            }
        }

        json_list.append(dictionary)
        framecount += 1

        cv2.waitKey(1)
        # print(pred)
    else:
        break
cap.release()
cv2.destroyAllWindows()
write_file(json_list, "effects.json")
