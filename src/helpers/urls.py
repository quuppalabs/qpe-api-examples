from dataclasses import dataclass
import urllib.parse as urlparse


@dataclass
class QpeUrlCompendium:
    """A class to manage urls of some QPE API endpoints"""

    base_url: str = "http://localhost:8080/qpe/"

    def __post_init__(self):
        self.locator_info_url = "/".join([self.base_url, "getLocatorInfo"])  # sdxfg
        self.peinfo_url = "/".join([self.base_url, "getPEInfo"])
        self.project_info_url = "/".join(
            [self.base_url, "getProjectInfo?version=2&noImageBytes=true"]
        )
        self.qpe_stop_mode = "/".join([self.base_url, "setQPEMode?mode=stop"])
        self.qpe_mode_track_url = "/".join([self.base_url, "setQPEMode?mode=track"])
        self.qpe_mode_deployment_url = "/".join(
            [self.base_url, "setQPEMode?mode=deployment"]
        )
        self.get_tag_data_defaultInfo = "/".join(
            [self.base_url, "getTagData?mode=json&format=defaultInfo"]
        )
        self.get_tag_data_defaultLocation = "/".join(
            [self.base_url, "getTagData?mode=json&format=defaultLocation"]
        )
        self.get_tag_data_defaultLocationAndInfo = "/".join(
            [self.base_url, "getTagData?mode=json&format=defaultLocationAndInfo"]
        )
        self.get_tag_data_all_items = "/".join(
            [self.base_url, "getTagData?mode=json&format=ALL_ITEMS"]
        )

    @staticmethod
    def update_url_query(url: str, query_params: dict) -> str:
        """takes a url and query string params and returns a new url with those query parameters in it

        Args:
            url (String): original url
            params (dict): query string parameters

        Returns:
            String: new url including query string parameters
        """
        url_parse = urlparse.urlparse(url)
        query = url_parse.query
        url_dict = dict(urlparse.parse_qsl(query))
        url_dict.update(query_params)
        url_new_query = urlparse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        new_url = urlparse.urlunparse(url_parse)

        return new_url
