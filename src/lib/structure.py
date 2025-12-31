"""
Document structure preservation utilities for the embedding pipeline.

This module provides functions for preserving document hierarchy and structure
during content extraction from Docusaurus sites.
"""
from typing import Dict, List, Any, Tuple
import re
from bs4 import BeautifulSoup


def preserve_document_hierarchy(soup: BeautifulSoup, max_depth: int = 6) -> List[Dict[str, Any]]:
    """
    Extract and preserve document hierarchy from BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the document
        max_depth: Maximum heading depth to consider (h1-h6)

    Returns:
        List of hierarchical structure information
    """
    hierarchy = []

    # Find all headings in document order
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    for heading in headings:
        level = int(heading.name[1])  # Extract number from h1, h2, etc.

        if level > max_depth:
            continue

        heading_info = {
            'level': level,
            'text': heading.get_text().strip(),
            'id': heading.get('id', ''),
            'class': heading.get('class', []),
            'content': []
        }

        # Find the next heading at the same or higher level
        next_heading = _find_next_heading(heading)

        # Extract content between this heading and the next one
        if next_heading:
            content = _extract_content_between(heading, next_heading)
        else:
            # If this is the last heading, extract content until end of relevant section
            content = _extract_content_after(heading)

        heading_info['content'] = content
        hierarchy.append(heading_info)

    return hierarchy


def _find_next_heading(current_heading) -> Any:
    """Find the next heading element after the current one."""
    for element in current_heading.find_next_siblings():
        if element.name and element.name.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return element
    return None


def _extract_content_between(start_element, end_element) -> List[Dict[str, Any]]:
    """Extract content between two elements."""
    content = []
    current = start_element.next_sibling

    while current and current != end_element:
        if hasattr(current, 'name') and current.name:
            content.append({
                'type': current.name,
                'text': current.get_text().strip(),
                'content': current.decode_contents() if hasattr(current, 'decode_contents') else str(current)
            })
        current = current.next_sibling

    return content


def _extract_content_after(start_element) -> List[Dict[str, Any]]:
    """Extract content after a given element."""
    content = []
    current = start_element.next_sibling

    while current:
        if hasattr(current, 'name') and current.name:
            content.append({
                'type': current.name,
                'text': current.get_text().strip(),
                'content': current.decode_contents() if hasattr(current, 'decode_contents') else str(current)
            })
        current = current.next_sibling

    return content


def create_document_outline(hierarchy: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a hierarchical document outline from heading information.

    Args:
        hierarchy: List of heading information from preserve_document_hierarchy

    Returns:
        Dictionary representing the document outline
    """
    if not hierarchy:
        return {'title': '', 'sections': []}

    # Use the first h1 as the document title
    title = ''
    sections = []

    for item in hierarchy:
        if item['level'] == 1 and not title:
            title = item['text']
        else:
            sections.append(item)

    return {
        'title': title,
        'sections': _build_nested_sections(sections)
    }


def _build_nested_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build nested section structure based on heading levels."""
    if not sections:
        return []

    nested = []
    current_level = sections[0]['level'] if sections else 0

    i = 0
    while i < len(sections):
        section = sections[i].copy()
        section['subsections'] = []

        current_level = section['level']
        i += 1

        # Add subsections that are at a deeper level
        while i < len(sections) and sections[i]['level'] > current_level:
            if sections[i]['level'] == current_level + 1:
                # Direct child, add it
                subsection = sections[i].copy()
                subsection['subsections'] = []
                section['subsections'].append(subsection)
                i += 1
            else:
                # Need to handle nested subsections
                break

        nested.append(section)

    return nested


def extract_content_by_heading_level(soup: BeautifulSoup, target_level: int) -> List[Dict[str, Any]]:
    """
    Extract content under headings of a specific level.

    Args:
        soup: BeautifulSoup object containing the document
        target_level: Heading level to target (e.g., 2 for h2)

    Returns:
        List of content blocks under each heading of the target level
    """
    results = []
    target_headings = soup.find_all(f'h{target_level}')

    for heading in target_headings:
        content_info = {
            'heading': heading.get_text().strip(),
            'id': heading.get('id', ''),
            'content': []
        }

        # Get content until the next heading of the same or higher level
        next_sibling = heading.next_sibling
        while next_sibling:
            if hasattr(next_sibling, 'name') and next_sibling.name and \
               next_sibling.name.lower().startswith('h') and \
               int(next_sibling.name[1]) <= target_level:
                break

            if hasattr(next_sibling, 'get_text'):
                content_info['content'].append({
                    'type': next_sibling.name if hasattr(next_sibling, 'name') else 'text',
                    'text': next_sibling.get_text().strip(),
                    'element': str(next_sibling) if hasattr(next_sibling, '__str__') else ''
                })

            next_sibling = next_sibling.next_sibling

        results.append(content_info)

    return results


def preserve_formatting_elements(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extract and preserve formatting elements like code blocks, lists, and tables.

    Args:
        soup: BeautifulSoup object containing the document

    Returns:
        List of formatting elements with their context
    """
    elements = []

    # Extract code blocks
    for code_block in soup.find_all(['code', 'pre']):
        elements.append({
            'type': 'code',
            'content': code_block.get_text().strip(),
            'language': _detect_language(code_block),
            'context': _get_context_around(code_block)
        })

    # Extract lists
    for list_elem in soup.find_all(['ul', 'ol']):
        items = [li.get_text().strip() for li in list_elem.find_all('li', recursive=False)]
        elements.append({
            'type': 'list',
            'items': items,
            'ordered': list_elem.name == 'ol',
            'context': _get_context_around(list_elem)
        })

    # Extract tables
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            row = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
            if row:
                rows.append(row)

        elements.append({
            'type': 'table',
            'rows': rows,
            'headers': rows[0] if rows else [],
            'context': _get_context_around(table)
        })

    return elements


def _detect_language(code_element) -> str:
    """Detect programming language from code element classes or content."""
    classes = code_element.get('class', [])
    if classes:
        for cls in classes:
            if 'language-' in cls:
                return cls.replace('language-', '')
            elif 'lang-' in cls:
                return cls.replace('lang-', '')

    # Default to text if no language detected
    return 'text'


def _get_context_around(element, context_size: int = 100) -> str:
    """Get surrounding text context for an element."""
    # Get parent text and extract a snippet around this element
    parent = element.find_parent()
    if parent:
        parent_text = parent.get_text()
        element_text = element.get_text()

        # Find the element text in parent text and get surrounding context
        pos = parent_text.find(element_text)
        if pos != -1:
            start = max(0, pos - context_size // 2)
            end = min(len(parent_text), pos + len(element_text) + context_size // 2)
            return parent_text[start:end].strip()

    return ''


def segment_content_by_headings(text: str, heading_patterns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Segment content by heading patterns without HTML parsing.

    Args:
        text: Plain text content to segment
        heading_patterns: List of regex patterns that represent headings

    Returns:
        List of content segments with heading information
    """
    if heading_patterns is None:
        # Default patterns for markdown-style headings
        heading_patterns = [
            r'^#{1,6}\s+(.+)',  # Markdown headings
            r'^(.+)\n={3,}$',   # Setext-style headings (underlined)
            r'^(.+)\n-{3,}$'    # Setext-style subheadings
        ]

    segments = []
    lines = text.split('\n')

    current_segment = {'heading': '', 'content': [], 'level': 0}

    for line in lines:
        is_heading = False

        for pattern in heading_patterns:
            match = re.match(pattern, line.strip(), re.MULTILINE)
            if match:
                # Save previous segment if it has content
                if current_segment['content'] or current_segment['heading']:
                    segments.append(current_segment)

                # Start new segment with this heading
                heading_text = match.group(1).strip()
                level = line.count('#') if line.strip().startswith('#') else 1

                current_segment = {
                    'heading': heading_text,
                    'content': [],
                    'level': level
                }
                is_heading = True
                break

        if not is_heading:
            current_segment['content'].append(line)

    # Add the last segment
    if current_segment['content'] or current_segment['heading']:
        segments.append(current_segment)

    return segments


def flatten_hierarchy(hierarchy: List[Dict[str, Any]], separator: str = '\n') -> str:
    """
    Flatten a document hierarchy into a single text string.

    Args:
        hierarchy: Document hierarchy from preserve_document_hierarchy
        separator: Separator to use between sections

    Returns:
        Flattened text representation of the hierarchy
    """
    flattened_parts = []

    for item in hierarchy:
        # Add heading
        heading_prefix = '#' * item['level'] + ' ' if item['level'] > 0 else ''
        flattened_parts.append(f"{heading_prefix}{item['text']}")

        # Add content
        for content_item in item['content']:
            if 'text' in content_item and content_item['text']:
                flattened_parts.append(content_item['text'])

    return separator.join(flattened_parts)