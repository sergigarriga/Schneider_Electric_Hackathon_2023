import os

# Access to all files in the current directory and subdirectories
for root, dirs, files in os.walk("."):
    for filename in files:
        # Check if the file has a zone identifier
        if filename.endswith(":Zone.Identifier"):
            # Delete the zone identifier
            os.remove(os.path.join(root, filename))
            print("Deleted zone identifier from file: " + os.path.join(root, filename))
