import socket
import xmlrpc.client

import pytest
from megamock import Mega, MegaMock, MegaPatch

from pytest_hot_reloading.client import PytestClient


class TestPytestClient:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self._server_proxy_mock = MegaPatch.it(
            xmlrpc.client.ServerProxy, spec_set=False
        ).megainstance

    def test_run(self, capsys: pytest.CaptureFixture) -> None:
        MegaPatch.it(PytestClient._start_daemon_if_needed)
        self._server_proxy_mock.run_pytest = MegaMock(
            return_value={
                "stdout": xmlrpc.client.Binary("stdout".encode("utf-8")),
                "stderr": xmlrpc.client.Binary("stderr".encode("utf-8")),
            }
        )
        client = PytestClient()
        args = ["foo", "bar"]

        client.run(args)

        out, err = capsys.readouterr()

        assert out == "stdout\n"
        assert err == "stderr\n"

    def test_aborting_should_close_the_socket(self) -> None:
        mock = MegaMock.it(PytestClient)
        Mega(mock.abort).use_real_logic()
        mock._socket = MegaMock.it(socket.socket)

        mock.abort()

        assert Mega(mock._socket.close).called_once()

    def test_aborting_the_socket_without_starting_should_not_error(self) -> None:
        PytestClient().abort()