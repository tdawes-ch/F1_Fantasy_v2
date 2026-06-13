race_id = 1289
session_name = "Qualifying Practice Lol"

session_id = f"{race_id}{session_name.split()}"
print(session_id)

test = f"{race_id}{"".join(word.lower()[0] for word in session_name.split(" "))}"
print(test)