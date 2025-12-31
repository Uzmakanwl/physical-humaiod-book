"""
Document structure preservation utilities for the embedding pipeline.

This module contains functions and classes for preserving document
structure during content extraction and processing.
"""

from typing import Dict, List, Any, Tuple
import re
from bs4 import BeautifulSoup


class DocumentStructure:
    """Represents the hierarchical structure of a document."""

    def __init__(self, title: str = "", url: str = ""):
        """
        Initialize a document structure.

        Args:
            title: The document title
            url: The source URL
        """
        self.title = title
        self.url = url
        self.headings = []  # List of (level, text, id) tuples
        self.content_blocks = []  # List of content blocks with their context
        self.metadata = {}
        self.breadcrumbs = []  # Hierarchical path to current content

    def add_heading(self, level: int, text: str, element_id: str = ""):
        """
        Add a heading to the document structure.

        Args:
            level: Heading level (1-6)
            text: Heading text
            element_id: Optional element ID
        """
        self.headings.append((level, text, element_id))

    def add_content_block(self, content: str, context: List[Tuple[int, str]] = None):
        """
        Add a content block with its hierarchical context.

        Args:
            content: The content block text
            context: List of (level, heading_text) tuples representing hierarchy
        """
        context = context or self.get_current_context()
        self.content_blocks.append({
            'content': content,
            'context': context.copy(),
            'heading_path': ' > '.join([heading for _, heading in context])
        })

    def get_current_context(self) -> List[Tuple[int, str]]:
        """
        Get the current hierarchical context based on headings.

        Returns:
            List of (level, heading_text) tuples
        """
        context = []
        for level, text, _ in self.headings:
            if level <= max([ctx[0] for ctx in context], default=0) if context else True:
                # Keep only headings at the same or higher level
                context = [(l, t) for l, t in context if l < level]
            context.append((level, text))
        return context

    def get_breadcrumb_path(self) -> str:
        """
        Get a breadcrumb-style path representing the document structure.

        Returns:
            Breadcrumb path as a string
        """
        return ' > '.join([text for _, text, _ in self.headings])

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the document structure to a dictionary.

        Returns:
            Dictionary representation of the document structure
        """
        return {
            'title': self.title,
            'url': self.url,
            'headings': [{'level': level, 'text': text, 'id': element_id}
                         for level, text, element_id in self.headings],
            'content_blocks': self.content_blocks,
            'metadata': self.metadata,
            'breadcrumb_path': self.get_breadcrumb_path()
        }


def preserve_document_structure(html_content: str) -> DocumentStructure:
    """
    Extract and preserve document structure from HTML content.

    Args:
        html_content: HTML content to analyze

    Returns:
        DocumentStructure object with preserved hierarchy
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    doc_structure = DocumentStructure()

    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        doc_structure.title = title_tag.get_text().strip()

    # Process headings and content in document order
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section', 'article']):
        if element.name.startswith('h') and len(element.name) == 2:
            # This is a heading
            level = int(element.name[1])
            text = element.get_text().strip()
            element_id = element.get('id', '')
            doc_structure.add_heading(level, text, element_id)
        elif element.name in ['p', 'div', 'section', 'article']:
            # This is content - preserve with current context
            content = element.get_text().strip()
            if content and len(content) > 20:  # Only add substantial content
                context = doc_structure.get_current_context()
                doc_structure.add_content_block(content, context)

    return doc_structure


def extract_section_hierarchy(content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract hierarchical sections from content data.

    Args:
        content_data: Content data with headings and text

    Returns:
        List of hierarchical sections
    """
    headings = content_data.get('headings', [])
    text_content = content_data.get('text_content', '')

    if not headings:
        # If no headings, return the entire content as one section
        return [{
            'level': 0,
            'title': content_data.get('title', 'Untitled'),
            'content': text_content,
            'path': [content_data.get('title', 'Untitled')]
        }]

    # Create a list of positions where headings occur in the text
    heading_positions = []
    for heading in headings:
        title = heading.get('text', '')
        pos = text_content.find(title)
        if pos != -1:
            heading_positions.append({
                'pos': pos,
                'level': heading.get('level', 0),
                'title': title,
                'id': heading.get('id', '')
            })

    # Sort by position in text
    heading_positions.sort(key=lambda x: x['pos'])

    sections = []
    for i, heading in enumerate(heading_positions):
        start_pos = heading['pos'] + len(heading['title'])
        end_pos = heading_positions[i + 1]['pos'] if i + 1 < len(heading_positions) else len(text_content)

        # Extract content between this heading and the next
        content = text_content[start_pos:end_pos].strip()

        # Build path based on hierarchy
        path = []
        for j, prev_heading in enumerate(heading_positions[:i+1]):
            if prev_heading['level'] <= heading['level'] or j == 0:
                # Only include headings at same or higher level, or the main title
                if not path or prev_heading['level'] <= path[-1]['level']:
                    path = [h for h in path if h['level'] < prev_heading['level']] + [prev_heading]

        sections.append({
            'level': heading['level'],
            'title': heading['title'],
            'content': content,
            'path': [h['title'] for h in path]
        })

    return sections


def create_contextual_chunks(sections: List[Dict[str, Any]], max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Create contextual chunks from hierarchical sections.

    Args:
        sections: List of hierarchical sections
        max_chunk_size: Maximum size of each chunk

    Returns:
        List of contextual chunks
    """
    chunks = []

    for section in sections:
        content = section['content']
        title = section['title']
        path = section['path']
        level = section['level']

        if len(content) <= max_chunk_size:
            # Content fits in a single chunk
            chunks.append({
                'content': content,
                'title': title,
                'context_path': ' > '.join(path),
                'hierarchy_level': level,
                'section_title': title
            })
        else:
            # Split content into smaller chunks
            paragraphs = re.split(r'\n\s*\n', content)
            current_chunk = ""
            current_chunk_size = 0

            for paragraph in paragraphs:
                if len(paragraph) > max_chunk_size:
                    # This paragraph is too large, we need to split it
                    sentences = re.split(r'[.!?]+', paragraph)
                    temp_chunk = ""
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        if len(temp_chunk) + len(sentence) <= max_chunk_size:
                            temp_chunk += sentence + ". "
                        else:
                            if temp_chunk:
                                chunks.append({
                                    'content': temp_chunk.strip(),
                                    'title': title,
                                    'context_path': ' > '.join(path),
                                    'hierarchy_level': level,
                                    'section_title': title
                                })
                            temp_chunk = sentence + ". "

                    if temp_chunk:
                        chunks.append({
                            'content': temp_chunk.strip(),
                            'title': title,
                            'context_path': ' > '.join(path),
                            'hierarchy_level': level,
                            'section_title': title
                        })
                else:
                    if current_chunk_size + len(paragraph) <= max_chunk_size:
                        current_chunk += paragraph + "\n\n"
                        current_chunk_size += len(paragraph) + 2
                    else:
                        if current_chunk.strip():
                            chunks.append({
                                'content': current_chunk.strip(),
                                'title': title,
                                'context_path': ' > '.join(path),
                                'hierarchy_level': level,
                                'section_title': title
                            })
                        current_chunk = paragraph + "\n\n"
                        current_chunk_size = len(paragraph) + 2

            # Add the last chunk if it has content
            if current_chunk.strip():
                chunks.append({
                    'content': current_chunk.strip(),
                    'title': title,
                    'context_path': ' > '.join(path),
                    'hierarchy_level': level,
                    'section_title': title
                })

    return chunks


def enhance_content_with_structure(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance content data with structural information.

    Args:
        content_data: Original content data

    Returns:
        Enhanced content data with structural information
    """
    # Extract hierarchical sections
    sections = extract_section_hierarchy(content_data)

    # Create contextual chunks
    chunks = create_contextual_chunks(sections)

    # Add structural information to the content data
    enhanced_data = content_data.copy()
    enhanced_data['structured_sections'] = sections
    enhanced_data['contextual_chunks'] = chunks
    enhanced_data['hierarchy_depth'] = max([s['level'] for s in sections], default=0) if sections else 0
    enhanced_data['section_count'] = len(sections)
    enhanced_data['chunk_count'] = len(chunks)

    return enhanced_data


def build_document_tree(headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a hierarchical tree structure from headings.

    Args:
        headings: List of headings with level, text, and id

    Returns:
        Hierarchical tree structure
    """
    if not headings:
        return []

    tree = []
    stack = []  # Stack to keep track of parent nodes

    for heading in headings:
        level = heading['level']
        text = heading['text']
        element_id = heading['id']

        node = {
            'level': level,
            'text': text,
            'id': element_id,
            'children': []
        }

        # Pop items from stack that are not ancestors of this node
        while stack and stack[-1]['level'] >= level:
            stack.pop()

        # If there's a parent in the stack, add this node as its child
        if stack:
            stack[-1]['children'].append(node)
        else:
            # This is a root-level heading
            tree.append(node)

        # Add this node to the stack
        stack.append(node)

    return tree


def flatten_tree(tree: List[Dict[str, Any]], parent_path: str = "") -> List[Dict[str, Any]]:
    """
    Flatten a tree structure to a list with full paths.

    Args:
        tree: Hierarchical tree structure
        parent_path: Path of parent nodes

    Returns:
        Flattened list with full paths
    """
    result = []
    for node in tree:
        current_path = f"{parent_path} > {node['text']}" if parent_path else node['text']
        result.append({
            'level': node['level'],
            'text': node['text'],
            'id': node['id'],
            'path': current_path
        })
        if node['children']:
            result.extend(flatten_tree(node['children'], current_path))
    return result