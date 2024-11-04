import os
import matplotlib.pyplot as plt
import re
import frontmatter
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
#from networkx.nx_agraph import graphviz_layout
#from networkx.drawing.nx_agraph import graphviz_layout


def extract_note_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        post = frontmatter.load(file)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        previous = post.get('previous', None)
        creation_datetime = post.get('created', None)
        #print(previous)
        if previous:
            previous = str(previous).replace('[', '').replace(']', '').strip()  # Remove wikilink brackets
        return filename, previous, creation_datetime

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

    # Create a directed graph
    G = nx.DiGraph()

    # Add a global graph attribute for nodesep
    G.graph['nodesep'] = '0.1'

    # Add nodes to the graph
    for note in notes:
        G.add_node(note['id'], label=note['filename'])

    # Add edges to the graph
    for note in notes:
        if note['next']:
            for next_note in note['next']:
                next_note_id = re.sub(r'\W+', '', next_note)
                G.add_edge(note['id'], next_note_id)

    # Get the coordinates for each node
    pos = graphviz_layout(G, prog='dot')
    pos = {k: (-v[1], v[0]) for k, v in pos.items()}  # Swap x and y coordinates and invert x for the opposite rotation

    # Print the coordinates and ids
    for node_id, coordinates in pos.items():
        for note in notes:
            if note['id'] == node_id:
                note['coordinates'] = (coordinates[0] * 10, coordinates[1] * 3)

    card_size = 400
    card_spacing = 100

    canvas_nodes = []
    canvas_edges = []

    for note in notes:
        note_id = note['id']
        note_x = note['coordinates'][0]
        note_y = note['coordinates'][1]
        note_name = note['filename']
        canvas_nodes.append(f'{{"id":"{note_id}","x":{note_x},"y":{note_y},"width":{card_size},"height":{card_size},"type":"file","file":"Thoughts/{note_name}.md"}}')
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

# Write the generated canvas to a canvas file
with open('/Users/vmitchell/Obsidian/Vault/Thoughts Canvas.canvas', 'w', encoding='utf-8') as file:
    file.write(thoughts_canvas)