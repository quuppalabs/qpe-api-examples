from src.helpers.urls import QpeUrlCompendium


def test_update_url_query():
    """tests if the function returns the correct URL string"""
    original_url = "http://localhost:8080/qpe/getTagData"
    final_url = "http://localhost:8080/qpe/getTagData?mode=json&format=defaultInfo"
    parameters = {"mode": "json", "format": "defaultInfo"}

    test_url = QpeUrlCompendium.update_url_query(original_url, parameters)

    assert test_url == final_url


def test_compendium_constructor():
    """tests that the url compendium correctly
    updates the base address
    """
    test_url = "http://localhost:8080/qpe/setQPEMode?mode=deployment"
    comp = QpeUrlCompendium("http://localhost:8080/qpe")

    assert test_url == comp.qpe_mode_deployment_url
