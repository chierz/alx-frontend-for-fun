#!/usr/bin/env python3

import sys
import os
import re
import hashlib

def convert_md_to_html(input_file, output_file):
    """Converts a Markdown file to an HTML file."""
    try:
        with open(input_file, 'r') as md_file:
            markdown_content = md_file.readlines()

        html_content = []
        is_list_open = None
        paragraph_lines = []

        for line in markdown_content:
            line = line.rstrip()

            # Handle headings
            heading_match = re.match(r'(#{1,6})\s+(.*)', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_content = heading_match.group(2).strip()
                close_open_list(html_content, is_list_open)
                is_list_open = None
                html_content.append(f"<h{level}>{heading_content}</h{level}>")
                continue  # Proceed to next line after heading

            # Handle unordered lists (-)
            elif line.startswith('- '):
                if is_list_open != "ul":
                    close_open_list(html_content, is_list_open)
                    is_list_open = "ul"
                    html_content.append("<ul>")
                list_item = convert_text_formatting(line[2:])
                html_content.append(f"<li>{list_item}</li>")

            # Handle ordered lists (*)
            elif line.startswith('* '):
                if is_list_open != "ol":
                    close_open_list(html_content, is_list_open)
                    is_list_open = "ol"
                    html_content.append("<ol>")
                list_item = convert_text_formatting(line[2:])
                html_content.append(f"<li>{list_item}</li>")

            # Handle empty lines (paragraph breaks)
            elif not line:
                if paragraph_lines:
                    close_open_list(html_content, is_list_open)
                    is_list_open = None
                    html_content.append(create_paragraph(paragraph_lines))
                    paragraph_lines.clear()
            else:
                # Convert [[text]] to MD5 and ((text)) to remove 'c'
                line = re.sub(r'\[\[(.*?)\]\]', lambda match: md5_hash(match.group(1)), line)
                line = re.sub(r'\(\((.*?)\)\)', lambda match: remove_char(match.group(1), 'c'), line)
                paragraph_lines.append(line)

        # Handle any remaining paragraph lines
        if paragraph_lines:
            close_open_list(html_content, is_list_open)
            html_content.append(create_paragraph(paragraph_lines))

        # Close any open list tags
        close_open_list(html_content, is_list_open)

        # Write the final HTML content to the output file
        with open(output_file, 'w') as html_file:
            html_file.write("\n".join(html_content))

    except FileNotFoundError:
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

def convert_text_formatting(text):
    """Convert Markdown bold and emphasis syntax to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)  # Bold
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)    # Emphasis
    return text

def md5_hash(text):
    """Convert the input text to its MD5 hash in lowercase."""
    return hashlib.md5(text.encode()).hexdigest()

def remove_char(text, char):
    """Remove all occurrences of a specified character from the text."""
    return text.replace(char, '').replace(char.upper(), '')

def create_paragraph(lines):
    """Creates a paragraph from a list of lines."""
    paragraph_text = ' '.join(lines).strip()

    # Handle <br/> between lines if multiple lines are present in the same paragraph
    paragraph_text = ' '.join(line if idx == 0 else f"<br/>{line}" for idx, line in enumerate(lines))
    paragraph_text = convert_text_formatting(paragraph_text)
    return f"<p>{paragraph_text}</p>"

def close_open_list(html_content, current_list):
    """Close the open list if needed."""
    if current_list == "ul":
        html_content.append("</ul>")
    elif current_list == "ol":
        html_content.append("</ol>")

def main():
    # Check if the correct number of arguments is passed
    if len(sys.argv) != 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if the markdown file exists
    if not os.path.isfile(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)

    # Call the conversion function
    convert_md_to_html(markdown_file, output_file)

if __name__ == "__main__":
    main()
