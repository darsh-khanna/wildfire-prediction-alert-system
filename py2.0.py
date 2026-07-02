import subprocess

# The group name and the message to send
group_name = "Jayanagar"
message = "90%"

# Call the Node.js script, passing group name and message as arguments
subprocess.run(["node", "test.js", group_name, message])
