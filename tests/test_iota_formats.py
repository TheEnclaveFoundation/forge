from forge.apps.cli_tools.iota.formats.obsidian import ObsidianFormatProvider

# --- Tests for create_link ---

def test_obsidian_link_creation():
    """Tests that the Obsidian provider can correctly format a wikilink."""
    provider = ObsidianFormatProvider()
    assert provider.create_link("My-Note", "My Note") == "[[My-Note|My Note]]"

def test_obsidian_link_creation_no_display_text():
    """Tests that the link is created correctly when the display text matches the target."""
    provider = ObsidianFormatProvider()
    assert provider.create_link("My-Note", "My-Note") == "[[My-Note]]"

# --- Tests for strip_formatting ---

def test_obsidian_strip_formatting():
    """Tests the stripping of wikilinks and backticks."""
    provider = ObsidianFormatProvider()
    original_text = "This is a `test` with a [[Link-Target|link]] and another [[Simple-Link]]."
    expected_text = "This is a test with a link and another Simple-Link."
    assert provider.strip_formatting(original_text) == expected_text

# --- Tests for find_links ---

def test_obsidian_find_links():
    """Tests finding all wikilinks in a piece of text."""
    provider = ObsidianFormatProvider()
    text = "A [[Link-One|link]] and [[Link-Two]]."
    
    found_links = list(provider.find_links(text))
    
    assert len(found_links) == 2
    # Check first link
    assert found_links[0].full_match == "[[Link-One|link]]"
    assert found_links[0].link_target == "Link-One"
    assert found_links[0].display_text == "link"
    # Check second link
    assert found_links[1].full_match == "[[Link-Two]]"
    assert found_links[1].link_target == "Link-Two"
    assert found_links[1].display_text == "Link-Two" # Should default to target