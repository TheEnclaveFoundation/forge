import re

def _strip_delta_example_markers(content: str) -> str:
    """
    Strips `#! DELTA_EXAMPLE::START/END` markers, preserving interior content literally.
    This regex captures content between example markers, including their newlines.
    It also accounts for potential leading/trailing whitespace on the marker lines themselves.
    """
    example_block_re = re.compile(
        r"^(?P<start_marker>\s*#! DELTA_EXAMPLE::START\s*)$\n" # Start marker line
        r"(?P<content_inside>.*?)\n"                           # Captured content (non-greedy, including newlines)
        r"^(?P<end_marker>\s*#! DELTA_EXAMPLE::END\s*)$",       # End marker line
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
    Orchestrates the processing of content for final output to a file or diff:
    1. Strips `#! DELTA_EXAMPLE::START/END` markers.
    2. Converts '@@@' markers to standard markdown code block fences ('```').
    """
    # Important: Stripping example markers must happen before converting @@@
    # so that @@@ inside example blocks are still converted.
    processed_content = _strip_delta_example_markers(content)
    processed_content = _convert_at_at_at_to_markdown_fences(processed_content)
    
    return processed_content