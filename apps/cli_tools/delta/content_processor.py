import re

def _strip_delta_example_markers(content: str) -> str:
    """
    Strips `#! DELTA_EXAMPLE::START/END` markers, preserving interior content literally.
    This regex captures content between example markers, including their newlines.
    It also accounts for potential leading/trailing whitespace on the marker lines themselves.
    """
    example_block_re = re.compile(
        r"^(?P<start_marker>\s*#! DELTA_EXAMPLE::START\s*)$\n"
        r"(?P<content_inside>.*?)\n"
        r"^(?P<end_marker>\s*#! DELTA_EXAMPLE::END\s*)$",
        re.MULTILINE | re.DOTALL
    )

    def replace_example_block(match):
        return match.group('content_inside')

    return example_block_re.sub(replace_example_block, content)

def _convert_at_at_at_to_markdown_fences(content: str) -> str:
    """
    Converts '@@@' markers to standard markdown code block fences ('```').
    - Replaces '@@@lang' at the start of a line with '```lang'
    - Replaces '@@@' on a line by itself with '```'
    """
    # Replace '@@@lang' at the start of a line with '```lang'
    content = re.sub(r"^\s*@@@(\S*)\s*$", r"```\1", content, flags=re.MULTILINE)
    # Replace '@@@' on a line by itself with '```'
    content = re.sub(r"^\s*@@@\s*$", r"```", content, flags=re.MULTILINE)
    
    return content

def process_content_for_output(content: str) -> str:
    """
    Orchestrates the processing of content for final output to a file or diff.
    Crucially, it converts '@@@' to backticks ONLY outside of `#! DELTA_EXAMPLE` blocks,
    while still removing the example markers themselves.
    """
    example_block_re = re.compile(
        r"^(?P<start_marker>\s*#! DELTA_EXAMPLE::START\s*)$\n"
        r"(?P<content_inside>.*?)\n"
        r"^(?P<end_marker>\s*#! DELTA_EXAMPLE::END\s*)$",
        re.MULTILINE | re.DOTALL
    )

    placeholders = {}
    def store_and_replace_example(match):
        placeholder = f"__DELTA_EXAMPLE_PLACEHOLDER_{len(placeholders)}__"
        # Store the raw, unprocessed content of the example block
        placeholders[placeholder] = match.group('content_inside')
        # Replace the entire example block (including markers) with the placeholder
        return placeholder

    # Isolate the example blocks
    content_with_placeholders = example_block_re.sub(store_and_replace_example, content)
    
    # Process the rest of the content (convert @@@ to ```)
    processed_content = _convert_at_at_at_to_markdown_fences(content_with_placeholders)

    # Substitute the raw, unprocessed example content back in
    for placeholder, original_content in placeholders.items():
        processed_content = processed_content.replace(placeholder, original_content)
        
    return processed_content