"""
You can auto-discover and run all tests with this command:

    $ pytest

Documentation:

* https://docs.pytest.org/en/latest/
"""

import src.standalone_scripts.auto_tag_config as tc


def test_update_url_query():
    """tests if the function returns the correct URL string"""
    original_url = "http://localhost:8080/qpe/getTagData"
    final_url = "http://localhost:8080/qpe/getTagData?mode=json&format=defaultInfo"
    parameters = {"mode": "json", "format": "defaultInfo"}

    test_url = tc.update_url_query(original_url, parameters)

    assert test_url == final_url
