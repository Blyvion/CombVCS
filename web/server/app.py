from asyncio import subprocess
import subprocess
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask_cors import CORS, cross_origin
import os
import pickle
from datetime import datetime
import json
import tensorflow as tf
import cv2
import numpy as np
import pandas as pd
from rank_bm25 import *
import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
lemmatizer = WordNetLemmatizer()

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SAVED_VIDEOS'] = "./static/saved_videos"
app.config['TEMPLATES_AUTO_RELOAD'] = True

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)


# BEGIN SERVER ENDPOINTS CODE
@app.route('/<filename>')
@cross_origin(origin='127.0.0.1', supports_credentials=True)
def load_page(filename):
	clear_timestamps = True
	if '~' in filename:
		filename = filename.split('~')[0]
		clear_timestamps = False

	write_template_file('./templates/index.html', filename, clear_timestamps)

	return render_template('index.html')

def write_template_file(path, filename, clear_timestamps):
	file = open(path, "r")
	html = file.read()
	ind1 = html.index("saved_videos/")+13
	ind2 = html.index("')}",ind1)
	oldname = html[ind1:ind2]

	html = html.replace(oldname, filename)

	if clear_timestamps:
		html = clear_timestamp_list(html)

	file = open(path, "w+")
	file.writelines(html)
	file.close()

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
	return jsonify('pong!')

# @app.route('/display/<filename>', methods=['GET'])
# @cross_origin(supports_credentials=True)
# def display_video(filename):
# 	#filename="video.mp4"
# 	#response = jsonify('127.0.0.1:5000/static/saved_videos/car2.mp4')
# 	return send_from_directory(
#         app.config['SAVED_VIDEOS'], filename, as_attachment=True
#     )

@app.route('/getvideo', methods=['POST'])
@cross_origin(origin='127.0.0.1', supports_credentials=True)
def get_video():
	response = {'status': 'success'}
	fName = request.data.decode("utf-8")
	file_name = "./static/saved_videos/"+fName

	file = open(file_name, "rb")
	file = file.read()
	response = file
	return response

@app.route('/deletevideo', methods=['POST'])
@cross_origin(origin='127.0.0.1', supports_credentials=True)
def delete_video():
	response = {'status': 'success'}
	fName = request.data.decode("utf-8")
	file_name = "./static/saved_videos/"+fName

	if(os.path.exists(file_name)):
		os.remove(file_name)
		response['message'] = 'video deleted'
	else:
		response['message'] = 'not found'

	return jsonify(response)

@app.route('/processvideo', methods=['POST'])
@cross_origin(origin='127.0.0.1', supports_credentials=True)
def process_video():
	response = {'status': 'success'}
	video = request.files['video']
	video_data = video.read()

	fName = video.filename

	out_file_name = "./static/saved_videos/"+fName

	with open(out_file_name, "wb") as out_file:
		out_file.write(video_data)
		out_file.close()

	output = execute_darknet(fName)
	execute_effects(fName)
	create_result_json(fName, output)
	combine_json_files(f"./{fName}", "./effects.json")
	# execute_ir(fName, "zss shields against cloud")
	# info_retrieval(fName, "zss shield against cloud")

	response['message'] = 'data received'
	return jsonify(response)

@app.route('/search', methods=['POST'])
@cross_origin(origin='127.0.0.1', supports_credentials=True)
def execute_search():
	text = request.form['text']
	filename = request.form['filename']
	info_retrieval(filename, text)
	create_timestamp_list(filename)
	return render_template('index.html')

@app.route('/listvideos', methods=['GET'])
@cross_origin(origin='127.0.0.1', supports_credentials=True)
def list_videos():
	response = {'status': 'success'}
	files = [name for name in os.listdir("./static/saved_videos") if name.lower().endswith(".mp4")]
	response['message'] = 'data received'
	response['videolist'] = files
	return jsonify(response)

# ========== TIMESTAMPS ==========

def write_timestamp_list(path, filename):
	file = open(path, "r")
	html = file.read()
	listItem = '<a class="list-group-item list-group-item-action" onclick="updateTimeStamp(\'#\')">$</a>'
	listContent = '<div id="tsList" class="card list-group" style="overflow-y: scroll;">'
	listItems = ''

	fName = "./static/saved_timestamps/"+filename[0:filename.rindex(".")] + ".txt"
	file = open(fName, "r")
	fileLines = file.readlines()

	for l in fileLines:
		lineSplit = l.split(',')
		stamp = lineSplit[0].replace(" ","").replace("\n","")
		cap = lineSplit[1].replace("\n","")
		listItems += listItem.replace('#',stamp).replace('$',(stamp + " " + cap))

	ind1List = html.index(listContent)+len(listContent)
	ind2List = html.index("</div>",ind1List)
	olddiv = html[ind1List:ind2List]

	if len(olddiv) > 0:
		html = html.replace(olddiv, listItems)
	else:
		html = html[:ind1List] + listItems + html[ind1List:]

	file = open(path, "w+")
	file.writelines(html)
	file.close()

def create_timestamp_list(filename):
	write_timestamp_list('./templates/index.html', filename)

def clear_timestamp_list(html):
	listContent = '<div id="tsList" class="card list-group" style="overflow-y: scroll;">'
	ind1List = html.index(listContent)+len(listContent)
	ind2List = html.index("</div>",ind1List)
	olddiv = html[ind1List:ind2List]
	html = html.replace(olddiv, '')
	return html

# ==============================

#BEGIN INFORMATION RETRIEVAL CODE
def addZeroIfLengthZero(metric):
	retMetric = ""
	if(len(metric) == 1):
		retMetric = "0"+metric
	else:
		retMetric = metric

	return retMetric

def get_cos_similarity(q, df):
	print("query:", q)
	# Convert the query become a vector
	q = [q]
	q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
	sim = {}
	# Calculate the similarity
	for i in range(len(df.columns)):
		sim[i] = np.dot(df.loc[:, i].values, q_vec) / np.linalg.norm(df.loc[:, i]) * np.linalg.norm(q_vec)

	# Sort the values
	sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)
	# Print the articles and their similarity values
	return sim_sorted


def info_retrieval(filename, query):
	from sklearn.metrics.pairwise import cosine_similarity
	v = cv2.VideoCapture(f"./static/saved_videos/{filename}")
	frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
	frame_rate = int(v.get(cv2.CAP_PROP_FPS))

	json_file = filename[0:filename.rindex(".")] + ".json"
	json = read_json(json_file)

	caps = pd.DataFrame(columns=['captions', 'frames'])
	i = 0
	for f in json:
		frm = f[('frame_'+str(i))]
		caption = (f"{frm['char1']['char']} {frm['char1']['move'].replace('_',' ')} {frm['char2']['char']} {frm['char2']['move'].replace('_',' ')} {frm['effect']}")
		caps.loc[len(caps.index)] = [caption, i]
		i+=1

	cap_vec = vectorizer.fit_transform(caps['captions']).toarray()
	query_vec = np.array(vectorizer.transform([query]).toarray())
	scores = list()
	for v in cap_vec:
		cs = cosine_similarity(query_vec, v.reshape(1, -1))
		scores.append(cs[0][0])
	caps['scores'] = scores
	caps = caps.sort_values('scores', ascending=False)
	caps = caps[caps['scores'] >= 0.5]

	timeStamps = list()

	i = 0
	for i in range(len(caps)):
		frame_index = caps['frames'].iloc[i]

		timeStamp = str(round((frame_index/100)/frame_rate,2))
		tsSplit = timeStamp.split('.')
		mins = int(tsSplit[0])
		secs = int(tsSplit[1])
		hours = 0

		if mins > 59:
			hours = mins/60
			mins = 0

			hoursSplit = str(hours).split('.')

			if len(hoursSplit) > 1:
				mins = int(float("."+hoursSplit[1])*60)

			hours = int(hoursSplit[0])

		if secs > 0:
			secs -= 1

		hours = addZeroIfLengthZero(str(hours))
		mins = addZeroIfLengthZero(str(mins))
		secs = addZeroIfLengthZero(str(secs))

		caption = caps['captions'].iloc[i]
		timeStamp = (str(hours)+":"+str(mins)+":"+str(secs))+","+caption
		#print("TIMESTAMP: "+timeStamp)

		if not timeStamp in timeStamps:
			timeStamps.append(timeStamp)
	fName = filename[0:filename.rindex(".")] + ".txt"
	fName = fName.replace("saved_videos","saved_timestamps")

	with open("./static/saved_timestamps/"+fName, 'w') as f:
		i = 0
		for ts in timeStamps:
			caption = caps['captions'].iloc[i]
			f.write(ts+"\n")
			i += 1
		f.close()





def execute_ir(filename,query):
	frame_code = "hufehfuaioehaiwlfherjwiaflbnejwailfgbeawuiolfhbaeruif" # Don't ask! I don't answer questions; I question answers!

# 	                                                .--____.
#                      ,_____._,                ,~-__,__,;\
#                    ,/ /  / /~,\              ~'-_ ,~_/__--\
#                  ,~'\/__:_; / ~\,_          /-__ ~\/  \";/,\
#                 / \ ,/\_\_~\ /  /|,';;;;`,|\  /\/     \=/- |
#                ~--,/_/__  \ ~\ |  `._____.'  |/\/     __---=--
#               /==/./ \ /\  ;\~\_\          _/\/,,__--'._/-' `
#              |==|/    \==\;  ;\|  , \ \ / /L /::/ \,~~ |==|-|
#              |//\\,__/== |: ;  |L_\  \ V / /L::/-__/  /=/-,|
#               \ / | | \ /: ;  ;\ |\\  \ / //|: |__\_/=/--/,,
#                \______,/; ;   ;;\ @|\  | /|@|;: \__\__\_/  ``,,
#                      ,;  ;   ;;;|\/' \ |/ '\/;;               '',=``,
#                     ,;  ;   ;;;;\  {  \|' }/;:'                  ,;;;
#                     ,;  ;  ;;;;;:| {   |  }|;'                    , ;;;
#                    ,; ;' ::::::;/    ./ \  \                        :, ""
#                   ,;;;;`,'`'`';/   ./    \  \_                       :,
#                   ,;;     '''|____/   \__/\___|                       :,
#                   ,;;             \_.  / _/                            :,
#                   ,;;                \/\/                               :,
#                   ,;;                                                    :,
#                   ,;;                                                    :,
#                   ,;;,                         ,--------.,       :;      :,
#                    `:';__--                   /       .   \,     :;      :,
#         .___________--`                      |        \    \___  :;      :,
#        /                                    |:        | ;  \  \ :;       :,
#       |                                     ;;;      / ;    |   :;      :.
#      |:                       /             ;;;     | ,;    |  :;    ,,:'
#      ;;;     /--;:,:;,,:;;;,;/';,,,,,,,,,,';;:    /  ;      |,;:,,,;:'
#      ;:;    |`"';;;';';;'';;;         |   ;;:     / :;      |;;;'  |
#      ;;    /                          |  ;;:     / :;-_____/   |   |
#      ;:   |                           / ;;:     / :;           |   \
#      ;     |                         |:,;;     | :;            /    |
#     ;      |                         /-;'   ':| ;:            |:,,;/
#     |:  ,;/                         |  ;      |:;             /-__-\
#      ;   |                          \  ::,,,:/:;             |      |
#      /   |                           \/`\    |:;             \  /\  /
#     /-____\                              |    \'              \/'`\/
#    |      `)                            /-____-\
#    | ^   /                             |        |
#    |/`\/                               |        |
#                                         \  /\  /
#                                          \/'`\/


	v = cv2.VideoCapture(f"./static/saved_videos/{filename}")
	frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
	frame_rate = int(v.get(cv2.CAP_PROP_FPS))
	#print(frames)
	# print(frame_rate)

	json_file = filename[0:filename.rindex(".")] + ".json"
	json = read_json(json_file)

	caps = pd.DataFrame(columns=['captions', 'frame number'])
	captions = []
	i = 0
	for f in json:
		frm = f[('frame_'+str(i))]
		# Added additional captions, so IR system can consider characters individually as well as together.
		# cap1 = (f"{frm['char1']['char']} {frm['char1']['move'].replace('_',' ')} {frm['effect']}")
		# cap2 = (f"{frm['char2']['char']} {frm['char2']['move'].replace('_',' ')} {frm['effect']}")
		caption = (f"{frm['char1']['char']} {frm['char1']['move'].replace('_',' ')} {frm['char2']['char']} {frm['char2']['move'].replace('_',' ')} {frm['effect']}")
		# caps.loc[len(caps.index)] = [cap1, i]
		# caps.loc[len(caps.index)] = [cap2, i]
		caps.loc[len(caps.index)] = [caption, i]
		# Caption augmentation (associate spike with down air???)
		i+=1

	# tokenized_corpus = [ lemmatize(doc) for doc in caps['captions'] ]

	# It fits the data and transform it as a vector
	X = vectorizer.fit_transform(caps['captions'])
	# Convert the X as transposed matrix
	X = X.T.toarray()
	# Create a DataFrame and set the vocabulary as the index
	df = pd.DataFrame(X, index=vectorizer.get_feature_names())

	# bm25 = BM25Okapi(tokenized_corpus)

	# tokenized_query = lemmatize(query)
	# doc_scores = bm25.get_scores(tokenized_query)
	# print(doc_scores)
	# caps['scores'] = doc_scores
	# caps = caps.sort_values('scores', ascending=False)
	# print(caps['scores'].head(5))
	# caps = caps[0:50]

	test = get_cos_similarity(query,df)
	print(test)
	# for k, v in test:
	# 	if v != 0.0:
	# 		print("Similaritas:", v)
	# 		print(caps['captions'][k])
	# 		print()

	timeStamps = set()

	i = 0
	for i in range(len(test)):
		frame_index = caps['frame number'].iloc[test[i][0]]
		#print("RANK:      #"+str(i))
		#print(f"FRAME:    {frame_index}")

		timeStamp = str(round((frame_index/100)/frame_rate,2))
		tsSplit = timeStamp.split('.')
		mins = int(tsSplit[0])
		secs = int(tsSplit[1])
		hours = 0

		if mins > 59:
			hours = mins/60
			mins = 0

			hoursSplit = str(hours).split('.')

			if len(hoursSplit) > 1:
				mins = int(float("."+hoursSplit[1])*60)

			hours = int(hoursSplit[0])

		hours = addZeroIfLengthZero(str(hours))
		mins = addZeroIfLengthZero(str(mins))
		secs = addZeroIfLengthZero(str(secs))

		caption = caps['captions'].iloc[test[i][0]]
		timeStamp = (str(hours)+":"+str(mins)+":"+str(secs))+","+caption
		#print("TIMESTAMP: "+timeStamp)

		timeStamps.add(timeStamp)
	fName = filename[0:filename.rindex(".")] + ".txt"
	fName = fName.replace("saved_videos","saved_timestamps")

	with open("./static/saved_timestamps/"+fName, 'w+') as f:
		i = 0
		for ts in timeStamps:
			caption = caps['captions'].iloc[i]
			f.write(ts+"\n")
			i += 1
		f.close()






def lemmatize(sentence):
	sentence = sentence.split(" ")
	i=0
	for w in sentence:
		sentence[i] = lemmatizer.lemmatize(w)
		i+=1
	return sentence

# BEGIN DARKNET/EFFECT MODEL CODE
def execute_darknet(video):
	bashCommand = f"./darknet/darknet detector demo ./darknet/data/obj.data ./darknet/yolov3_move_train.cfg ./yolov3_move_train_last.weights ./static/saved_videos/{video} -thresh 0.3 -dont_show -ext_output > result.txt"
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()
	return output.decode("utf-8")

def execute_effects(video):
	command = f"python3 effect_detector.py {video}"
	subprocess.Popen(command.split(), stdout=subprocess.PIPE).communicate()

# BEGIN DARKNET OUTPUT TRANSFORMER CODE
def check_dupe(line1, line2):
	str1 = line1.split(" ")[0]
	str2 = line2.split(" ")[0]
	if(str1 == str2):
		if(str1 is '' and str2 is ''):
			return True
		else:
			return False
	else:
		return True

def write_dictionary(char1, move1, char2, move2, frame):
	dictionary = {
		f"frame_{frame}":{
			"char1":{
				"char" : char1,
				"move" : move1,
			},
			"char2":{
				"char" : char2,
				"move" : move2,
			}
		}
	}
	return dictionary

def read_json(filename):
	with open(filename, 'r') as json_file:
		json_data = json.load(json_file)
		return json_data

def write_file(dictionaries, filename):
	with open(filename, 'w+') as json_file:
		data = dictionaries
		jsoned_data = json.dumps(data, indent=True)
		json_file.write(jsoned_data)

def create_result_json(filename, lines):
	json_file = filename[0:filename.rindex(".")] + ".json"

	lines = lines.split('\n')
	ONE, TWO = False, False
	filter1Lines = list()
	for count in range(len(lines)):
		if('%' in lines[count]):
			if(not ONE):
				ONE = True
				# print('ONE')
			elif(not TWO):
				TWO = True
				# print('TWO')

			# print(lines[count])
			filter1Lines.append(lines[count])
		elif ('FPS' in lines[count]):
			if(not ONE and not TWO):
				filter1Lines.append(" : ")
				filter1Lines.append(" : ")
				# count = count + 1
			elif(ONE and not TWO):
				filter1Lines.append(" : ")
				ONE = False
			elif(ONE or TWO):
				ONE, TWO = False, False

	filter1Lines = [x.split(":")[0] for x in filter1Lines]

	filter2Lines = list()
	frameCount = 0
	for i in range(0, len(filter1Lines), 2):
		str = ""
		str += filter1Lines[i] + f" {frameCount}"  + "|"
		if(i+1 < len(filter1Lines)):
			if(check_dupe(filter1Lines[i], filter1Lines[i+1])):
				#if its not a match
				str += filter1Lines[i+1]+ f" {frameCount}"
			filter2Lines.append(str)
			frameCount+=1

	filter2Lines = [x.replace(" ", ",") for x in filter2Lines]

	dictList = list()
	for x in filter2Lines:
		char = x.split("|")
		char1 = char[0].split(",")
		if(len(char[1]) != 0):
			char2 = char[1].split(",")
			dictList.append(write_dictionary(char1[0], char1[1],char2[0], char2[1], char1[2]))
		else:
			dictList.append(write_dictionary(char1[0], char1[1],"","", char1[2]))

	write_file(dictList, json_file)


def combine_json_files(frame_data_file, effect_data_file):
	frame_data_file = frame_data_file[0:frame_data_file.rindex(".")] + ".json"
	frame_data_json = read_json(frame_data_file)
	effect_data_json = read_json(effect_data_file)

	length = len(frame_data_json) if len(frame_data_json) <= len(effect_data_json) else len(effect_data_json)
	combined_list = list()
	for i in range(length):
		frame_key = f"frame_{i}"
		effect_key = f"frame_{i}"
		frame_data = frame_data_json[i]
		effect_data = effect_data_json[i]
		frame_data = frame_data[frame_key]
		effect_data = effect_data[effect_key]
		combined_data = { frame_key: { "char1": frame_data["char1"], "char2": frame_data["char2"], "effect": effect_data["effect"] } }
		# print(combined_data)
		combined_list.append(combined_data)

	write_file(combined_list, frame_data_file)


if __name__ == '__main__':
	app.run(host=os.environ.get('COMBVCS_HOST', '127.0.0.1'), port=int(os.environ.get('COMBVCS_PORT', '32001')))

# _________  ________      _____ ______________   _____________   _________
# \_   ___ \ \_____  \    /     \\______   \   \ /   /\_   ___ \ /   _____/
# /    \  \/  /   |   \  /  \ /  \|    |  _/\   Y   / /    \  \/ \_____  \
# \     \____/    |    \/    Y    \    |   \ \     /  \     \____/        \
#  \______  /\_______  /\____|__  /______  /  \___/    \______  /_______  /
#         \/         \/         \/       \/                   \/        \/
