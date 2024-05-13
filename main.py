import json
import urllib.request

def request(action, **params):
  return { "action": action, "params": params, "version": 6 }

def invoke(action, **params):
	requestJson = json.dumps(request(action, **params)).encode("utf-8")
	response = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8765", requestJson)))
	if len(response) != 2:
		raise Exception("The response has an unexpected number of fields.")
	if "error" not in response:
		raise Exception("The response is missing a required error field.")
	if "result" not in response:
		raise Exception("The response is missing a required result field.")
	if response["error"] is not None:
		raise Exception(response["error"])
	return response["result"]

def tag_note(id, tags):
	invoke("updateNote", note = {
		"id": id,
		"tags": tags
	})

def find_unknown_kanjis(file_name):
	unknown_kanjis = []
	with open(file_name) as file:
		kanji_grid = json.load(file)["units"]
		for kanji in kanji_grid:
			if kanji_grid[kanji][2] + kanji_grid[kanji][3] == 0:
				unknown_kanjis.append(kanji)
	return unknown_kanjis

def is_useless_word(word, unknown_kanjis):
	for unknown_kanji in unknown_kanjis:
		if unknown_kanji in word:
			return False
	return True

def main(deck_name, word_field, kanji_grid_path):
	unknown_kanjis = find_unknown_kanjis(kanji_grid_path)
	note_ids = invoke("findNotes", query = "deck:{} is:new".format(deck_name))
	notes = invoke("notesInfo", notes = note_ids)
	for i in range(0, len(notes)):
		word = notes[i]["fields"][word_field]["value"]
		if is_useless_word(word, unknown_kanjis):
			tag_note(notes[i]["noteId"], ["useless"])
		else:
			tag_note(notes[i]["noteId"], ["useful"])
		print("{}/{} - {}".format(i + 1, len(notes), word))

#################################
######### Settings ##############
#################################

# The name of the deck to query.
deck_name = "日本語"

# The field that the word will be read from.
word_field = "Word"

# The file path of the exported kanji grid.
kanji_grid_path = "kanji_grid.json"

main(deck_name, word_field, kanji_grid_path)
