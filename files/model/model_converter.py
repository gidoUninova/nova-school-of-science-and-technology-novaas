import zipfile
import os
import shutil
import xml.etree.ElementTree as ET
import json
import glob

# Prompt the user for input paths
# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))
# Find all .aasx files in the script's directory
aasx_files = glob.glob(os.path.join(script_directory, "*.aasx"))

# Ensure there's exactly one .aasx file
if len(aasx_files) == 0:
    raise FileNotFoundError("No .aasx file found in the script directory.")
elif len(aasx_files) > 1:
    raise FileExistsError("Multiple .aasx files found in the script directory. Please specify which one to use.")
else:
    aasx_file_path = aasx_files[0]  # Use the only .aasx file found

# Define the updated .aasx file path with "_converted" appended
base_name = os.path.splitext(os.path.basename(aasx_file_path))[0]  # Extract the base name
dist_directory = os.path.join(script_directory, "")
updated_aasx_file_path = os.path.join("..", "model.aasx")
# Ensure the 'dist' directory exists
os.makedirs(dist_directory, exist_ok=True)

rels_file_name = 'aasx-origin.rels'

# Step 1: Verify if the .aasx file is a valid ZIP archive
if not zipfile.is_zipfile(aasx_file_path):
    print(f"The file '{aasx_file_path}' is not a valid ZIP archive or is corrupted.")
    exit()

# Step 2: Create a /temp directory inside the current directory
current_dir = os.getcwd()  # Get the current working directory
output_dir = os.path.join(current_dir, 'temp')  # Define the /temp directory
os.makedirs(output_dir, exist_ok=True)  # Create the /temp directory if it doesn't already exist

print(f"Temporary directory created at: {output_dir}")

# Step 3: Unzip the .aasx file into the /temp directory
try:
    with zipfile.ZipFile(aasx_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"Unzipped successfully to: {output_dir}")
except Exception as e:
    print(f"An error occurred during unzipping: {e}")
    exit()

# Additional processing can go here (e.g., modifying .rels, replacing files, etc.)
    
#Step 5: Replace the .xml file with a .json file
try:
   # Define the target folder to search within
    target_folder = os.path.join(output_dir, "aasx")

    # Search for .xml files specifically within the "aasx" folder and its subdirectories
    xml_files = glob.glob(os.path.join(target_folder, '**', '*.xml'), recursive=True)
        
    if not xml_files:
        print("No XML file found to replace. Cleaning up temporary files...")
        shutil.rmtree(output_dir)
        print("Temporary files cleaned up.")
        exit()

    # Assuming only one XML file for replacement
    original_xml_file_path = xml_files[0]  # Take the first XML file found
    print(f"Found XML file to replace: {original_xml_file_path}")
    testPath = os.path.basename(original_xml_file_path)
    new_json_file_name = testPath.replace('.xml', '.json')  # Replace .xml with .json
    print(f"New JSON file name: {new_json_file_name}")


    # Step 2: Define the path to the existing JSON file
    # Find all .json files in the script directory
    json_directory = os.path.join(output_dir, "aasx")
    json_files = glob.glob(os.path.join(json_directory, "*.json"))

    # Ensure there's exactly one .json file
    if len(json_files) == 0:
        print("No .json file found in the script directory. Exiting the program.")
        exit()
    elif len(json_files) > 1:
        raise FileExistsError("Multiple .json files found in the script directory. Please specify which one to use.")
        exit()
    else:
        existing_json_file_path = json_files[0]  # Use the only .json file found
        print(f"Using JSON file: {existing_json_file_path}")
    
    
    # Step 3: Copy the JSON file to the same location as the XML file, using testPath as the new name
    new_json_file_path = os.path.join(os.path.dirname(original_xml_file_path), new_json_file_name)
    shutil.copy(existing_json_file_path, new_json_file_path)
    print(f"Copied JSON file to: {new_json_file_path}")
    relative_json_path = os.path.relpath(new_json_file_path)
    relative_json_path = relative_json_path.replace("temp/", "")
    print(f"Relative path to JSON file: {relative_json_path}")

    # Step 4: Delete the original XML file
    os.remove(original_xml_file_path)
    print(f"Removed original XML file: {original_xml_file_path}")

except FileNotFoundError as fnfe:
    print(f"Error: {fnfe}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()
    
# Step 3: Locate the .rels file
rels_file_path = os.path.join(output_dir, 'aasx/_rels', rels_file_name)
print(f"Found .rels file at: {rels_file_path}")
if not os.path.exists(rels_file_path):
    print(f"The .rels file '{rels_file_name}' was not found in the expected location: {rels_file_path}")
    exit()

# Step 4: Modify the .rels file
aasx_file_name = os.path.basename(aasx_file_path)
new_json_file_name = aasx_file_name.replace('.aasx', '.json')

try:
    tree = ET.parse(rels_file_path)
    root = tree.getroot()
    namespace = "http://schemas.openxmlformats.org/package/2006/relationships"
    ET.register_namespace('', namespace)

    found_xml = False
    found_json = False

    # Check for any Target that ends with .xml or .json
    for relationship in root.findall(f'{{{namespace}}}Relationship'):
        target = relationship.get('Target')  # Get the Target attribute
        if target.endswith('.xml'):  # Check if the Target ends with .xml
            found_xml = True
            # Update the Target to the new .json file path
            relationship.set('Target', f"/{relative_json_path}")
        elif target.endswith('.json'):  # Check if the Target ends with .json
            found_json = True

    if found_json and not found_xml:
        print("Found .json target in the .rels file. No action needed. Exiting the program.")
        exit()

    if found_xml:
        # Write the updated .rels file if .xml targets were modified
        tree.write(rels_file_path, encoding='utf-8', xml_declaration=True)
        print(f"Updated .rels file: {rels_file_path}")
    else:
        print("No .xml or .json targets found in the .rels file. Exiting the program.")
        exit()

except Exception as e:
    print(f"An error occurred while modifying the .rels file: {e}")
    exit()

# Step 6: Rezip the updated content into a new .aasx file
try:
    with zipfile.ZipFile(updated_aasx_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root_dir, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                archive_name = os.path.relpath(file_path, output_dir)  # Preserve folder structure in the archive
                zip_ref.write(file_path, archive_name)
    print(f"Updated .aasx file created in parent directory: {updated_aasx_file_path}")
except Exception as e:
    print(f"An error occurred during zipping: {e}")
    exit()

# Step 7: Clean up the temporary unzipped content
try:
    shutil.rmtree(output_dir)
    print("Temporary files cleaned up.")
except Exception as e:
    print(f"An error occurred during cleanup: {e}")