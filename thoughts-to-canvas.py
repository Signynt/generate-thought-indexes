import os
import re
import frontmatter

card_width = 400
card_height = 400
vertical_gap = 100
horizontal_gap = 200

def extract_note_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        post = frontmatter.load(file)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        previous = post.get('previous', None)
        creation_datetime = post.get('created', None)
        if previous:
            previous = str(previous).replace('[', '').replace(']', '').strip()  # Remove wikilink brackets
        return filename, previous, creation_datetime

def create_block(node, nodes_dict, vertical_gap=vertical_gap):
    children = []
    if node['next']:
        for child_filename in node['next']:
            child = nodes_dict[child_filename]
            child = create_block(child, nodes_dict)
            children.append(child)
    if not children:
        children = None
    node['children'] = children
    node['height'] = sum([child['height'] for child in children]) + (len(children) - 1) * vertical_gap if children else card_height
    return node

def layout_blocks(nodes, x=0, y=0, vertical_gap=vertical_gap, horizontal_gap=horizontal_gap):
    current_x = x
    current_y = y

    for node in nodes:
        node['coordinates'] = {'x': current_x, 'y': current_y}
        if node['children']:
            layout_blocks(node['children'], current_x + card_width + horizontal_gap, current_y, vertical_gap, horizontal_gap)
        current_y += node['height'] + vertical_gap

def auto_layout(nodes):
    nodes_dict = {node['filename']: node for node in nodes}
    roots = [node for node in nodes if node['previous'] is None]
    root_blocks = [create_block(root, nodes_dict) for root in roots]
    layout_blocks(root_blocks)
    return nodes

def generate_canvas(folder_path):
    notes = []

    # Iterate through the files in the specified folder
    for file in os.listdir(folder_path):
        if file.endswith('.md'):  # filter for markdown files
            file_path = os.path.join(folder_path, file)
            filename, previous, creation_datetime = extract_note_info(file_path)
            notes.append({
                'filename': filename,
                'previous': previous,
                'creation_datetime': creation_datetime
            })
        
    # Add a dictionary filed called 'next' to each note, which lists the notes that reference it as 'previous'
    for note in notes:
        next_notes = [n['filename'] for n in notes if n['previous'] == note['filename']]
        note['next'] = next_notes if next_notes else None
        # Generate a unique id for each note
        note['id'] = re.sub(r'\W+', '', note['filename'])

    # Sort notes by creation_datetime
    notes = sorted(notes, key=lambda x: x['creation_datetime'])

    notes = auto_layout(notes)

    canvas_nodes = []
    canvas_edges = []

    for note in notes:
        note_id = note['id']
        note_x = note['coordinates']['x']
        note_y = note['coordinates']['y']
        note_name = note['filename']
        canvas_nodes.append(f'{{"id":"{note_id}","x":{note_x},"y":{note_y},"width":{card_width},"height":{card_height},"type":"file","file":"Thoughts/{note_name}.md"}}')
        if note['previous']:
            # Get the id of the previous note
            previous_id = re.sub(r'\W+', '', note['previous'])
            canvas_edges.append(f'{{"id":"{note_id}","fromNode":"{previous_id}","fromSide":"right","toNode":"{note_id}","toSide":"left"}}')

    nodes_store_full = ",\n\t\t\t".join(canvas_nodes)
    edges_store_full = ",\n\t\t\t".join(canvas_edges)
    text = '''{
        "nodes":[
            '''+ nodes_store_full + '''
        ],
        "edges":[
            ''' + edges_store_full + '''
        ]
    }'''
    return text

folder_path = "/Users/vmitchell/Obsidian/Vault/Thoughts"

# Generate the Obsidian canvas
thoughts_canvas = generate_canvas(folder_path)

# Check if any changes would be made
canvas_file_path = '/Users/vmitchell/Obsidian/Vault/Thoughts Canvas.canvas'

if os.path.exists(canvas_file_path):
    with open(canvas_file_path, 'r', encoding='utf-8') as file:
        existing_content = file.read()
    if existing_content == thoughts_canvas:
        #print("No changes detected. The canvas file is up to date.")
        pass
    else:
        with open(canvas_file_path, 'w', encoding='utf-8') as file:
            file.write(thoughts_canvas)
        #print("Changes detected. The canvas file has been updated.")
else:
    with open(canvas_file_path, 'w', encoding='utf-8') as file:
        file.write(thoughts_canvas)
    #print("Canvas file created.")