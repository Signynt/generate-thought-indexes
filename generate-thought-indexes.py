import os
import yaml
from datetime import datetime
from collections import defaultdict

def parse_frontmatter(file_content):
    frontmatter = {}
    if file_content.startswith('---'):
        end = file_content.find('---', 3)
        if end != -1:
            frontmatter = yaml.safe_load(file_content[3:end])
    return frontmatter

def extract_metadata(folder_path):
    metadata = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                frontmatter = parse_frontmatter(content)
                if frontmatter:
                    tags = frontmatter.get('tags', [])
                    tag_list = []
                    for tag in tags:
                        split_tags = tag.split('/')
                        tag_list.append(split_tags)
                    filename = filename[:-3]
                    entry = {
                        'name': filename,
                        'tags': tag_list,
                        'created': frontmatter.get('created', ''),
                        'modified': frontmatter.get('modified', '')
                    }
                    metadata.append(entry)
    return metadata

def organize_by_category(metadata):
    category_dict = defaultdict(lambda: defaultdict(list))
    for entry in metadata:
        for tag_list in entry['tags']:
            current_level = category_dict
            for tag in tag_list:
                if tag not in current_level:
                    current_level[tag] = defaultdict(list)
                current_level = current_level[tag]
            current_level['files'].append(entry)
    return category_dict

def format_output(metadata):
    def format_category(category, indent=0):
        lines = []
        subcategories = []
        files = []
        for key, value in sorted(category.items()):
            if key == 'files':
                files = sorted(value, key=lambda x: x['created'])
            else:
                subcategories.append((key, value))
        
        for subcategory, subcategory_value in subcategories:
            lines.append(' ' * indent + '- ' + subcategory)
            lines.extend(format_category(subcategory_value, indent + 4))
        
        for file_entry in files:
            lines.append(' ' * indent + '- [[' + file_entry['name'] + ']]')
        
        return lines

    category_dict = organize_by_category(metadata)
    return format_category(category_dict)

def sorted_by_created(metadata):
    sorted_metadata = sorted(metadata, key=lambda x: x['created'])
    creation_time_list = ['- [[' + entry['name'] + ']]' for entry in sorted_metadata]
    return creation_time_list

def main():
    folder_path = '/Users/vmitchell/Obsidian/Vault/Thoughts'

    file_start_tags = '''---
BC-list-note-field: down
BC-list-note-exclude-index: true
BC-list-note-neighbour-field: next-tags
---'''

    file_start_creation_time = '''---
BC-list-note-field: down
BC-list-note-exclude-index: true
BC-list-note-neighbour-field: next
---'''

    metadata = extract_metadata(folder_path)
    tags_output_file_path = '/Users/vmitchell/Obsidian/Vault/Thought Index Tags.md'
    creation_time_output_file_path = '/Users/vmitchell/Obsidian/Vault/Thought Index Creation Time.md'

    tag_list = format_output(metadata)
    tag_list.insert(0, file_start_tags)

    creation_time_list = sorted_by_created(metadata)
    creation_time_list.insert(0, file_start_creation_time)

    if not os.path.exists(creation_time_output_file_path) or open(creation_time_output_file_path, 'r', encoding='utf-8').read() != "\n".join(creation_time_list):
        with open(creation_time_output_file_path, 'w', encoding='utf-8') as creation_time_output_file:
            creation_time_output_file.write("\n".join(creation_time_list))
    
    if not os.path.exists(tags_output_file_path) or open(tags_output_file_path, 'r', encoding='utf-8').read() != "\n".join(tag_list):
        with open(tags_output_file_path, 'w', encoding='utf-8') as tags_output_file:
            tags_output_file.write("\n".join(tag_list))

if __name__ == "__main__":
    main()