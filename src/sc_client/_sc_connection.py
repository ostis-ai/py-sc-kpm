from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any, Callable

# noinspection PyPackageRequirements
import websocket

from sc_client.constants import common, config
from sc_client.exceptions import PayloadMaxSizeError
from sc_client.models import Response, ScAddr, ScEvent


class ScConnection:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_open = False
        self.lock_instance = threading.Lock()
        self.responses_dict = {}
        self.events_dict = {}
        self.command_id = 0
        self.ws_app: websocket.WebSocketApp | None = None
        self.error_handler: Callable[[Exception], None] = self.default_error_handler
        self.reconnect_callback: Callable[[], None] = self.default_reconnect_handler
        self.post_reconnect_callback: Callable[[], None] = lambda *args: None
        self.reconnect_retries: int = config.SERVER_RECONNECT_RETRIES
        self.reconnect_retry_delay: float = config.SERVER_RECONNECT_RETRY_DELAY
        self.last_healthcheck_answer: str | None = None

    def establish_connection(self, url) -> None:
        def run_in_thread():
            self.ws_app = websocket.WebSocketApp(
                url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            self._logger.info(f"Sc-server socket: {self.ws_app.url}")
            try:
                self.ws_app.run_forever()
            except websocket.WebSocketException as e:
                self._on_error(self.ws_app, e)

        client_thread = threading.Thread(target=run_in_thread, name="sc-client-session-thread")
        client_thread.start()
        time.sleep(config.SERVER_ESTABLISH_CONNECTION_TIME)

        if self.is_open:
            self.post_reconnect_callback()

    def default_reconnect_handler(self) -> None:
        self.establish_connection(self.ws_app.url)

    @staticmethod
    def default_error_handler(error: Exception) -> None:
        raise error

    def _on_message(self, _, response: str) -> None:
        self._logger.debug(f"Receive: {str(response)[:config.LOGGING_MAX_SIZE]}")
        response = Response.load(response)
        if response.event:
            threading.Thread(
                target=self._emit_callback,
                args=(response.id, response.payload),
            ).start()
        else:
            self.responses_dict[response.id] = response

    def _emit_callback(self, event_id: int, elems: list[int]) -> None:
        event = self.events_dict.get(event_id)
        if event:
            event.callback(*[ScAddr(addr) for addr in elems])

    def _on_open(self, _) -> None:
        self._logger.info("New connection opened")
        self.is_open = True

    def _on_error(self, _, error: Exception) -> None:
        self.error_handler(error)

    def _on_close(self, _, _close_status_code, _close_msg) -> None:
        self._logger.info("Connection closed")
        self.is_open = False

    def set_error_handler(self, callback) -> None:
        self.error_handler = callback

    def set_reconnect_handler(
        self, reconnect_callback, post_reconnect_callback, reconnect_retries: int, reconnect_retry_delay: float
    ) -> None:
        self.reconnect_callback = reconnect_callback
        self.post_reconnect_callback = post_reconnect_callback
        self.reconnect_retries = reconnect_retries
        self.reconnect_retry_delay = reconnect_retry_delay

    def set_connection(self, url: str) -> None:
        self.establish_connection(url)

    def is_connected(self) -> bool:
        return self.is_open

    def close_connection(self) -> None:
        try:
            self.ws_app.close()
            self.is_open = False
        except AttributeError as e:
            self._on_error(self.ws_app, e)

    def receive_message(self, command_id: int) -> Response:
        while command_id not in self.responses_dict and self.is_open:
            time.sleep(config.SERVER_ANSWER_CHECK_TIME)
        return self.responses_dict[command_id]

    def _send_message(self, data: str, retries: int, retry: int = 0) -> None:
        try:
            self._logger.debug(f"Send: {data[:config.LOGGING_MAX_SIZE]}")
            self.ws_app.send(data)
        except websocket.WebSocketConnectionClosedException:
            if self.reconnect_callback and retry < retries:
                self._logger.warning(
                    f"Connection to sc-server has failed. "
                    f"Trying to reconnect to sc-server socket in {self.reconnect_retry_delay} seconds"
                )
                if retry > 0:
                    time.sleep(self.reconnect_retry_delay)
                self.reconnect_callback()
                self._send_message(data, retries, retry + 1)
            else:
                self._on_error(self.ws_app, ConnectionAbortedError("Sc-server takes a long time to respond"))

    def send_message(self, request_type: common.ClientCommand, payload: Any) -> Response:
        with self.lock_instance:
            self.command_id += 1
            command_id = self.command_id
        data = json.dumps(
            {
                common.ID: command_id,
                common.TYPE: request_type.value,
                common.PAYLOAD: payload,
            }
        )
        len_data = len(bytes(data, "utf-8"))
        if len_data > config.MAX_PAYLOAD_SIZE:
            self._on_error(
                self.ws_app, PayloadMaxSizeError(f"Data is too large: {len_data} > {config.MAX_PAYLOAD_SIZE} bytes")
            )
        self._send_message(data, self.reconnect_retries)
        response = self.receive_message(command_id)
        if not response:
            self._on_error(self.ws_app, ConnectionAbortedError("Sc-server takes a long time to respond"))
        return response

    def get_event(self, event_id: int) -> ScEvent | None:
        return self.events_dict.get(event_id)

    def drop_event(self, event_id: int):
        del self.events_dict[event_id]

    def set_event(self, sc_event: ScEvent) -> None:
        self.events_dict[sc_event.id] = sc_event
