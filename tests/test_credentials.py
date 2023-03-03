import pytest

from telethon.sessions.sqlite import SQLiteSession

from . import TEST_DATA_PATH
from ezee_tg import models


class TestCredentials:
    def test_client_meta_info(self):
        path = TEST_DATA_PATH / "mocks" / "credentials" / "6281515551247" / "6281515551247.json"
        model = models.ClientMetaInfo.from_file(path)
        assert model.app_id == 8
        assert model.app_hash == "7245de8e747a0d6fbe11f7cc14fcc0bb"

    def test_client_meta_info_no_file(self):
        path = TEST_DATA_PATH / "mocks" / "credentials" / "6281515551247" / "6281515551247eawq.json"
        try:
            model = models.ClientMetaInfo.from_file(path)
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Случай с отсутствующим файлом мета информации клиента не обработался")
            raise e

        assert False, f"Случай с отсутствующим файлом мета информации клиента не обработался"

    def test_credentials(self):
        path = TEST_DATA_PATH / "mocks" / "credentials" / "6281515551247"
        model = models.Credentials.from_file(path)
        assert model.client_meta == models.ClientMetaInfo(app_id=8, app_hash="7245de8e747a0d6fbe11f7cc14fcc0bb")
        assert type(model.session) == SQLiteSession

    def test_credentials_no_folder(self):
        path = TEST_DATA_PATH / "mocks" / "credentials" / "6281515551247qwe"
        try:
            model = models.Credentials.from_file(path)
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Случай с отсутствующей папкой не обработался")
            raise e

        assert False, f"Случай с отсутствующей папкой не обработался"

    def test_credentials_no_session(self):
        path = TEST_DATA_PATH / "mocks" / "credentials" / "6281515551248"
        model = models.Credentials.from_file(path)


