from tokenize import group
import zipfile
import os
import shutil
import xml.etree.ElementTree as ET
import json
import base64
import os
import glob
import uuid

# Function to convert a string to Base64
def covertIdB64(text):
    return base64.b64encode(text.encode()).decode()

# extract_observed_elements

def extract_observed_elements(data):
    observed_elements = []
    for element in data:
        if element.get("modelType") == "SubmodelElementCollection" or element.get("modelType") == "SubmodelElementList":
            observed_elements.extend(extract_observed_elements(element.get("value", [])))
        elif element.get("modelType") == "BasicEventElement":
            observed = element.get("observed", {}).get("keys", [])
            filtered_values = ".".join(
                key["value"] for key in observed if key["type"] not in ["AssetAdministrationShell", "Submodel"]
            )
            observed_elements.append(filtered_values)
    
    return observed_elements

def transform_path(input_string):
    parts = input_string.split(".")
    result = []

    for i, part in enumerate(parts):
        if part.isdigit() and i > 0:
            # Convert number to index on the previous string
            prev = result.pop()
            result.append(f"{prev}[{part}]")
        else:
            result.append(part)

    return ".".join(result)

def process_flows(model_json_path):
    """
    Processes model JSON and flows JSON, updating PropertyLink, PropertyLinkEvt,
    and switch rules dynamically.

    Returns:
        str: Path of the updated JSON file.
    """
    
    print(f"Using JSON file: {model_json_path}")

    # Load model.json
    with open(model_json_path, "r", encoding="utf-8") as model_file:
        model_data = json.load(model_file)

    # Extract AAS ID and convert it to Base64
    aas_id = model_data["assetAdministrationShells"][0]["id"]
    aas_id_b64 = covertIdB64(aas_id)
    print("AAS ID:", aas_id)
    print("AAS ID b64:", aas_id_b64)

    # Extract submodel OperationalData and convert its ID to Base64
    submodelOpDataIdB64 = ""
    aas_opdata = None
    observed_elements = []
    for submodel in model_data.get("submodels", []):
        #if submodel.get("idShort") == "OperationalData":
        submodelOpDataIdB64 = covertIdB64(submodel["id"])
        aas_opdata = submodel.get("submodelElements", [])
        #print("aas_opdata", aas_opdata)
        row = []
        row.append(submodelOpDataIdB64)
        row.append(extract_observed_elements(aas_opdata))
        observed_elements.append(row)
        print("observed_elements", observed_elements)
        #break  # Stop after finding the first match

    print("Operational Data ID b64:", submodelOpDataIdB64)

    # Locate flows_gido-VirtualBox.json in the parent directory
    
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    grandparent_dir = os.path.dirname(parent_dir)
    print(f"Parent directory: {grandparent_dir}")
    flows_json_path = os.path.join(grandparent_dir, "flows_gido-VirtualBox.json")

    # Load flows_gido-VirtualBox.json
    with open(flows_json_path, "r", encoding="utf-8") as flows_file:
        flows_data = json.load(flows_file)

    # Ensure the correct structure before iterating
    if isinstance(flows_data, dict):
        nodes = flows_data.get("nodes", [])  # Handle case where "nodes" is inside a dictionary
    elif isinstance(flows_data, list):
        nodes = flows_data  # If it's already a list, use it directly
    else:
        raise TypeError("Unexpected data format in flows_gido-VirtualBox.json")

    # Store new PropertyLink and PropertyLinkEvt values for switch rules
    new_values = []
    print("Processing nodes...")
    # Find and replace "PropertyLink" and "PropertyLinkEvt" inside "subflow:41b3a1439ccec2c1"
    #index = 0
    #for node in nodes:
    #    if node.get("type") == "subflow:41b3a1439ccec2c1":  # Check subflow type
    #        if index < len(observed_elements):  
    #            property_name_value = observed_elements[index]  # Safe access
    #            index += 1
    #        else:
    #            property_name_value = ""

            # Now, replace "PropertyLink" and "PropertyLinkEvt" using the extracted values
    #        for env_var in node.get("env", []):
    #            if property_name_value == "":
    #                if env_var.get("name") == "PropertyName":
    #                    property_name_value = env_var.get("value")
    #            elif env_var.get("name") == "PropertyName":
    #                new_value = f"{property_name_value}"
    #               print(f"Replacing PropertyName in node {node['id']} with {new_value}")
    #                env_var["value"] = new_value  # Replace with new formatted value
    #            if env_var.get("name") == "PropertyLink":
    #                new_value = f"{aas_id_b64}/{submodelOpDataIdB64}/{property_name_value}"
    #                print(f"Replacing PropertyLink in node {node['id']} with {new_value}")
    #                env_var["value"] = new_value  # Replace with new formatted value
    #                new_values.append(new_value)  # Store for switch rule updates
    #            elif env_var.get("name") == "PropertyLinkEvt":
    #                new_evt_value = f"{aas_id_b64}/{submodelOpDataIdB64}/{property_name_value}Evt"
    #                print(f"Replacing PropertyLinkEvt in node {node['id']} with {new_evt_value}")
    #                env_var["value"] = new_evt_value  # Replace with new formatted value

    # Find the "switch" node and update its rules with the new values
    for node in nodes:
        if node.get("type") == "switch" and node.get("property") == "payload.link":
            print(f"Updating switch node {node['id']} with {len(observed_elements)} rules")
            node["rules"] = [{"t": "eq", "v": "activeSubscriptions", "vt": "str"}]
            for row in observed_elements:
                if(len(row[1]) > 0):
                    for value in row[1]:
                        node["rules"].append({"t": "eq", "v": f"{aas_id_b64}/{row[0]}/{transform_path(value)}", "vt": "str"})
                        print(f"Adding rule for {aas_id_b64}/{row[0]}/{transform_path(value)}")
    # Removing inject_nodes
    #get tab id
    group = [node for node in nodes if node.get("type") == "group" and node.get("id") == "6aa9beecbf5f8d23"]
    tab_id = group[0]["z"]
    print("Tab id:", tab_id)
    inject_nodes = [node for node in nodes if node.get("type") == "inject" and node.get("topic") == "command" and node.get("z") in tab_id and node.get("g") == "6aa9beecbf5f8d23"]
    print("Inject nodes:", inject_nodes)
    for inject_node in inject_nodes:
        nodes.remove(inject_node)
        group[0]["nodes"].remove(inject_node["id"])
    # Adding an inject node for each observed_elements
    counter = 0
    for row in observed_elements:
        if(len(row[1]) > 0):
            for val in row[1]:
                new_inject_node_id = uuid.uuid4().hex[:16]
                inject_node = {
                    "id": new_inject_node_id,
                    "type": "inject",
                    "z": tab_id,
                    "g": "6aa9beecbf5f8d23",
                    "name": "",
                    "props": [
                        {
                            "p": "payload"
                        },
                        {
                            "p": "topic",
                            "vt": "str"
                        }
                    ],
                    "repeat": "",
                    "crontab": "",
                    "once": False,
                    "onceDelay": 0.1,
                    "topic": "command",
                    "payload": str(counter),
                    "payloadType": "num",
                    "x": 250,
                    "y": 360 + counter*40,
                    "wires": [
                        [
                            "1c9bb22c58e8a418"
                        ]
                    ]
                }
                nodes.append(inject_node)
                group[0]["nodes"].append(new_inject_node_id)
                counter += 1
    print(group[0])
            
    print("Processing complete.")
    # Save the modified JSON back to file
    updated_flows_file = os.path.basename(flows_json_path).replace(".json", "_updated.json")
    with open(flows_json_path, "w", encoding="utf-8") as updated_flows_file:
        json.dump(nodes, updated_flows_file, indent=4)

    print(f"Updated JSON file saved as {updated_flows_file}")
    print("Finalized updating base64 id and properties")


############################    MAIN SCRIPT    ############################
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
updated_aasx_file_path = os.path.join(".", "model.aasx")
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

######################### ------Unzipping the AASX Finalized---------################################

# Additional processing can go here (e.g., modifying .rels, replacing files, etc.)
    
#Step 5: Replace the .xml file with a .json file
try:
   # Define the target folder to search within
    target_folder = os.path.join(output_dir, "aasx")

    # Search for .xml files specifically within the "aasx" folder and its subdirectories
    xml_files = glob.glob(os.path.join(target_folder, '**', '*.xml'), recursive=True)
        
    if not xml_files:
        print("No XML file found to replace. Copying the original .aasx file to the parent directory...")
        try:
            # Copy the original .aasx file to the parent directory
            shutil.copy(aasx_file_path, updated_aasx_file_path)
            print(f"Original .aasx file copied to: {updated_aasx_file_path}")
        except Exception as e:
            print(f"An error occurred while copying the .aasx file: {e}")
        finally:
            # Clean up the temporary files
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
    # Find all .json files in the script directory and inside all other folders inside the directory
 # Find all .json files in the script directory
    json_directory = os.path.join(output_dir, "aasx")
    print(f"JSON directory: {json_directory}")

    json_files = glob.glob(os.path.join(json_directory, "**/*.json"))
    print(f"JSON files: {json_files}")
    print(f"Number of JSON files: {len(json_files)}")

    # Ensure there's at least one JSON file
    if len(json_files) == 0:
        print("No .json file found in the script directory. Exiting the program now.")
        print("Trying in the subdirectory")
        json_files = glob.glob(os.path.join(json_directory, "**", "*.json"), recursive=True)

    # Print found JSON files
    print(f"JSON files found: {json_files}")
    print(f"Number of JSON files: {len(json_files)}")

    # Ensure there's at least one JSON file
    if len(json_files) == 0:
        print("No .json file found in the script directory or subdirectories. Exiting the program now.")
        exit()
    elif len(json_files) > 1:
        print("Warning: Multiple .json files found. Using the first one.")

    # Use the first found JSON file
    existing_json_file_path = json_files[0]
    print(f"Using JSON file: {existing_json_file_path}")

    # Process flows with the selected JSON file
    process_flows(existing_json_file_path)
    
    
    # Step 3: Copy the JSON file to the same location as the XML file, using testPath as the new name
    new_json_file_path = os.path.join(os.path.dirname(original_xml_file_path), new_json_file_name)
    shutil.move(existing_json_file_path, new_json_file_path)
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
                # Step 7: Clean up the temporary unzipped content
        try:
            shutil.rmtree(output_dir)
            print("Temporary files cleaned up.")
        except Exception as e:
            print(f"An error occurred during cleanup: {e}")
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

# Extract base name of original AASX file and modify output name
base_name = os.path.splitext(os.path.basename(aasx_file_path))[0]
new_aasx_filename = f"model.aasx" 
backup_file_path = f"{aasx_file_path}.bak"
try:
    print("Trying to backup orignal aasx")
    shutil.copy2(aasx_file_path, backup_file_path)
    print(f"✅ Original file backed up as: {backup_file_path}")
except Exception as e:
    print(f"❌ Failed to create backup: {e}")
    exit()

try:
    with zipfile.ZipFile(updated_aasx_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root_dir, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                archive_name = os.path.relpath(file_path, output_dir)  # Preserve folder structure in the archive
                zip_ref.write(file_path, archive_name)
    print(f"✅ Updated .aasx file created: {updated_aasx_file_path}")

    # Step 7: Delete the original .aasx file after successful processing
    original_file_name = os.path.basename(aasx_file_path)
    if original_file_name != "model.aasx":
        if os.path.exists(aasx_file_path):
            os.remove(aasx_file_path)
            print(f"🗑️ Deleted original .aasx file: {aasx_file_path}")
        else:
            print(f"⚠️ Warning: Original .aasx file not found for deletion: {aasx_file_path}")
    else:
        print(f"🔒 Original file is named 'model.aasx', so it was not deleted.")

except Exception as e:
    print(f"❌ An error occurred during zipping: {e}")
    exit()

# Step 7: Clean up the temporary unzipped content
try:
    shutil.rmtree(output_dir)
    print("Temporary files cleaned up.")
except Exception as e:
    print(f"An error occurred during cleanup: {e}")