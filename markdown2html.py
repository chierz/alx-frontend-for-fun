#!/usr/bin/env python3

"""
markdown2html.py

A script that converts a Markdown file to an HTML file.

Usage:
    ./markdown2html.py <markdown_file> <output_file>

Arguments:
    markdown_file: The Markdown file to read from.
    output_file: The output HTML file to write to.

Error Handling:
    - If the number of arguments is less than 2, it prints an error message.
    - If the Markdown file doesn't exist, it prints a missing file error.
"""

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
        is_list_open = None  # Track if a list is open
        paragraph_lines = []  # To gather lines for paragraphs

        for line in markdown_content:
            line = line.strip()

            # Handle headings
            if line.startswith('#'):
                level = line.count('#')
                heading_content = line[level:].strip()
                close_open_list(html_content, is_list_open)
                html_content.append(f"<h{level}>{heading_content}</h{level}>")

            # Handle unordered lists
            elif line.startswith('* '):
                close_open_list(html_content, is_list_open)
                is_list_open = "ul"
                if not html_content or not html_content[-1].endswith('<ul>'):
                    html_content.append("<ul>")
                list_item = convert_text_formatting(line[2:])
                html_content.append(f"    <li>{list_item}</li>")

            # Handle ordered lists (if needed in the future)
            elif line.startswith('1. '):
                close_open_list(html_content, is_list_open)
                is_list_open = "ol"
                if not html_content or not html_content[-1].endswith('<ol>'):
                    html_content.append("<ol>")
                list_item = convert_text_formatting(line[3:])
                html_content.append(f"    <li>{list_item}</li>")

            # Handle paragraph breaks
            elif not line:
                if paragraph_lines:
                    html_content.append(create_paragraph(paragraph_lines))
                    paragraph_lines.clear()
            else:
                # Convert [[text]] to MD5 and ((text)) to remove 'c'
                line = re.sub(r'\[\[(.*?)\]\]', lambda match: md5_hash(match.group(1)), line)
                line = re.sub(r'\(\((.*?)\)\)', lambda match: remove_char(match.group(1), 'c'), line)
                paragraph_lines.append(line)

        # Handle any remaining paragraph lines
        if paragraph_lines:
            html_content.append(create_paragraph(paragraph_lines))

        # Close any open list tags
        if is_list_open:
            html_content.append(f"</{is_list_open}>")

        # Wrap the HTML content in <html> and <body> tags
        final_html_content = "<html>\n<body>\n" + "\n".join(html_content) + "\n</body>\n</html>"

        with open(output_file, 'w') as html_file:
            html_file.write(final_html_content)

    except FileNotFoundError:
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)


def convert_text_formatting(text):
    """Convert Markdown bold and emphasis syntax to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)  # Bold
    return re.sub(r'__(.+?)__', r'<em>\1</em>', text)   # Emphasis


def md5_hash(text):
    """Convert the input text to its MD5 hash in lowercase."""
    return hashlib.md5(text.encode()).hexdigest()


def remove_char(text, char):
    """Remove all occurrences of a specified character from the text."""
    return text.replace(char, '').replace(char.upper(), '')


def create_paragraph(lines):
    """Creates a paragraph from a list of lines."""
    paragraph_text = ' '.join(lines).strip()
    paragraph_text = convert_text_formatting(paragraph_text)
    return f"<p>\n{paragraph_text}\n</p>"


def close_open_list(html_content, current_list):
    """Close the open list if needed."""
    if current_list == "ul":
        html_content.append("</ul>")
    elif current_list == "ol":
        html_content.append("</ol>")


def main():
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_md_to_html(markdown_file, output_file)


if __name__ == "__main__":
    main()
