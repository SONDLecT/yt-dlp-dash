#!/usr/bin/env python3
"""
Parse yt-dlp options from documentation and generate comprehensive UI components
"""

import re
import json
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_ytdlp_options(file_path):
    """Parse the yt-dlp options markdown file and extract all options"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Categories and their options
    categories = {}
    current_category = None
    current_options = []
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for category header (e.g., "## General Options:")
        if line.startswith('## ') and line.endswith(':'):
            # Save previous category
            if current_category:
                categories[current_category] = current_options
            
            current_category = line[3:-1]  # Remove "## " and ":"
            current_options = []
        
        # Check for option line (starts with --)
        elif line.strip().startswith('-'):
            option_data = {
                'short': None,
                'long': None,
                'description': [],
                'type': 'flag',  # flag, string, number, choice
                'choices': None,
                'default': None,
                'aliases': []
            }
            
            # Parse the option line
            parts = line.strip().split(None, 1)
            if len(parts) >= 1:
                flags = parts[0].split(',')
                
                for flag in flags:
                    flag = flag.strip()
                    if flag.startswith('--'):
                        option_data['long'] = flag[2:]
                    elif flag.startswith('-') and len(flag) == 2:
                        option_data['short'] = flag[1]
                
                # Check if option takes an argument
                if len(parts) > 1 and parts[1]:
                    remaining = parts[1].strip()
                    
                    # Check for argument type indicators
                    if remaining.startswith('[') or remaining.upper().startswith(('PATH', 'URL', 'PREFIX', 'NAMES', 'FORMAT', 'TEMPLATE', 'SIZE', 'RATE')):
                        option_data['type'] = 'string'
                        if 'NUMBER' in remaining or 'COUNT' in remaining or 'SIZE' in remaining:
                            option_data['type'] = 'number'
                
                # Collect description from following lines
                i += 1
                while i < len(lines) and lines[i].startswith('                                    '):
                    desc_line = lines[i].strip()
                    option_data['description'].append(desc_line)
                    
                    # Check for choices in description
                    if 'Supported' in desc_line or 'Valid' in desc_line:
                        # Try to extract choices
                        choice_match = re.findall(r'(?:Supported|Valid)[^:]*:\s*([^.]+)', desc_line)
                        if choice_match:
                            choices = [c.strip() for c in choice_match[0].split(',')]
                            option_data['choices'] = choices
                            option_data['type'] = 'choice'
                    
                    # Check for default value
                    if 'default' in desc_line.lower():
                        default_match = re.search(r'\(default:?\s*([^)]+)\)', desc_line)
                        if default_match:
                            option_data['default'] = default_match.group(1)
                    
                    # Check for aliases
                    if 'Alias:' in desc_line:
                        alias_match = re.search(r'Alias:\s*([^)]+)', desc_line)
                        if alias_match:
                            option_data['aliases'].append(alias_match.group(1))
                    
                    i += 1
                
                i -= 1  # Adjust for the outer loop increment
                
                option_data['description'] = ' '.join(option_data['description'])
                
                if option_data['long'] or option_data['short']:
                    current_options.append(option_data)
        
        i += 1
    
    # Save last category
    if current_category:
        categories[current_category] = current_options
    
    return categories

def generate_ui_components(categories):
    """Generate HTML/JS for all options"""
    
    html_parts = []
    js_parts = []
    
    for category, options in categories.items():
        category_id = category.replace(' ', '').replace('-', '')
        
        # Start category section
        html_parts.append(f'''
<div class="option-category" id="category-{category_id}">
    <h3>{category}</h3>
    <div class="options-grid">''')
        
        for option in options:
            option_id = (option['long'] or option['short'] or '').replace('-', '_')
            
            if option['type'] == 'flag':
                # Checkbox for boolean flags
                html_parts.append(f'''
        <div class="option-item">
            <div class="checkbox-group">
                <input type="checkbox" id="opt_{option_id}" data-option="{option['long'] or option['short']}">
                <label for="opt_{option_id}">
                    {option['long'] or option['short']}
                    {f"(-{option['short']})" if option['short'] else ""}
                </label>
            </div>
            <small class="option-description">{option['description'][:200]}...</small>
        </div>''')
            
            elif option['type'] == 'choice':
                # Dropdown for choice options
                html_parts.append(f'''
        <div class="option-item">
            <label for="opt_{option_id}">{option['long'] or option['short']}</label>
            <select id="opt_{option_id}" data-option="{option['long'] or option['short']}">
                <option value="">Default</option>''')
                
                if option['choices']:
                    for choice in option['choices']:
                        html_parts.append(f'''
                <option value="{choice}">{choice}</option>''')
                
                html_parts.append(f'''
            </select>
            <small class="option-description">{option['description'][:200]}...</small>
        </div>''')
            
            elif option['type'] == 'number':
                # Number input
                html_parts.append(f'''
        <div class="option-item">
            <label for="opt_{option_id}">{option['long'] or option['short']}</label>
            <input type="number" id="opt_{option_id}" data-option="{option['long'] or option['short']}" 
                   placeholder="{option['default'] or ''}" class="option-input">
            <small class="option-description">{option['description'][:200]}...</small>
        </div>''')
            
            else:  # string
                # Text input
                html_parts.append(f'''
        <div class="option-item">
            <label for="opt_{option_id}">{option['long'] or option['short']}</label>
            <input type="text" id="opt_{option_id}" data-option="{option['long'] or option['short']}" 
                   placeholder="{option['default'] or ''}" class="option-input">
            <small class="option-description">{option['description'][:200]}...</small>
        </div>''')
        
        html_parts.append('''
    </div>
</div>''')
    
    return '\n'.join(html_parts)

def main():
    # Use relative paths based on script location
    input_file = os.path.join(SCRIPT_DIR, 'yt-dlp-options.md')
    json_output = os.path.join(SCRIPT_DIR, 'ytdlp_options.json')
    html_output = os.path.join(SCRIPT_DIR, 'templates', 'all_options.html')

    categories = parse_ytdlp_options(input_file)

    # Save parsed options as JSON for reference
    with open(json_output, 'w') as f:
        json.dump(categories, f, indent=2)

    # Generate UI components
    ui_html = generate_ui_components(categories)

    # Save UI components
    with open(html_output, 'w') as f:
        f.write(ui_html)
    
    print(f"Parsed {len(categories)} categories with {sum(len(opts) for opts in categories.values())} total options")
    for cat, opts in categories.items():
        print(f"  {cat}: {len(opts)} options")

if __name__ == '__main__':
    main()