import json

print("start")
bigobject = json.JSONEncoder().encode({"foo": ["bar", "baz"]})

for chunk in json.JSONEncoder().iterencode(bigobject):
    print(chunk)
print("start")
