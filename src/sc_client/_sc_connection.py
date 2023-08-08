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
        self._ws_app: websocket.WebSocketApp | None = None
        self._url: str | None = None
        self._lock = threading.Lock()
        self._responses_dict = {}
        self._events_dict: dict[int, ScEvent] = {}
        self._command_id = 0
        self._error_handler: Callable[[Exception], None] = self._default_error_handler
        self._on_reconnect: Callable[[], None] = self._default_reconnect_handler
        self._post_reconnect_callback: Callable[[], None] = self._default_post_reconnect_callback
        self.reconnect_retries: int = config.SERVER_RECONNECT_RETRIES
        self.reconnect_delay: float = config.SERVER_RECONNECT_RETRY_DELAY

    def connect(self, url: str) -> None:
        self._url = url
        client_thread = threading.Thread(target=self._run_ws_app, name="sc-client-session-thread")
        client_thread.start()
        time.sleep(config.SERVER_ESTABLISH_CONNECTION_TIME)

        if self.is_connected:
            self._post_reconnect_callback()

    def _run_ws_app(self) -> None:
        self._ws_app = websocket.WebSocketApp(
            self._url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._logger.info(f"Sc-server socket: {self._ws_app.url}")
        try:
            self._ws_app.run_forever()
        except websocket.WebSocketException as e:
            self._ws_app = None
            self._logger.error(e, exc_info=True)
            self._error_handler(e)

    def disconnect(self) -> None:
        try:
            self._ws_app.close()
        except AttributeError as e:
            self._logger.error(e, exc_info=True)
            raise e

    @property
    def is_connected(self) -> bool:
        return self._ws_app is not None

    def reconnect(self) -> None:
        self.connect(self._url)
        self._on_reconnect()

    def _on_message(self, _: websocket.WebSocketApp, response: str) -> None:
        self._logger.debug(f"Receive: {str(response)[:config.LOGGING_MAX_SIZE]}")
        response = Response.load(response)
        if response.event:
            if event := self.get_event(response.id):
                threading.Thread(
                    name=f"sc-event-{response.id}-thread",
                    target=event.callback,
                    args=(ScAddr(addr) for addr in response.payload),
                ).start()
        else:
            self._responses_dict[response.id] = response

    def _on_open(self, _: websocket.WebSocketApp) -> None:
        self._logger.info("New connection opened")

    def _on_error(self, _: websocket.WebSocketApp, error: Exception) -> None:
        self._logger.error(error)
        self._error_handler(error)

    def _on_close(self, _: websocket.WebSocketApp, *__) -> None:
        self._logger.info("Connection closed")
        self._ws_app = None

    def set_error_handler(self, callback) -> None:
        self._error_handler = callback

    def set_reconnect_handler(
        self,
        reconnect_callback: Callable[[], None] = None,
        post_reconnect_callback: Callable[[], None] = None,
        reconnect_retries: int = None,
        reconnect_retry_delay: float = None,
    ) -> None:
        self._on_reconnect = reconnect_callback or self._on_reconnect
        self._post_reconnect_callback = post_reconnect_callback or self._post_reconnect_callback
        self.reconnect_retries = reconnect_retries or self.reconnect_retries
        self.reconnect_delay = reconnect_retry_delay or self.reconnect_delay

    def receive_message(self, command_id: int) -> Response:
        while (answer := self._responses_dict.get(command_id)) is None:  # and self.is_connected
            time.sleep(config.SERVER_ANSWER_CHECK_TIME)
        return answer

    def _send_message(self, data: str, retries: int) -> None:
        while True:
            if self.is_connected:
                self._ws_app.send(data)
                self._logger.debug(f"Send: {data[:config.LOGGING_MAX_SIZE]}")
                return
            if retries:
                self._logger.warning(
                    f"Connection to sc-server has failed. "
                    f"Trying to reconnect to sc-server socket in {self.reconnect_delay} seconds"
                )
                if not retries:
                    raise ConnectionAbortedError("Sc-server takes a long time to respond")
                time.sleep(self.reconnect_delay)
                retries -= 1
                self.reconnect()

    def send_message(self, request_type: common.ClientCommand, payload: Any) -> Response:
        with self._lock:
            self._command_id += 1
            command_id = self._command_id
        data = json.dumps(
            {
                common.ID: command_id,
                common.TYPE: request_type.value,
                common.PAYLOAD: payload,
            }
        )
        len_data = len(bytes(data, "utf-8"))
        if len_data > config.MAX_PAYLOAD_SIZE:
            raise PayloadMaxSizeError(f"Data is too large: {len_data} > {config.MAX_PAYLOAD_SIZE} bytes")
        self._send_message(data, self.reconnect_retries)
        response = self.receive_message(command_id)
        if not response:
            raise ConnectionAbortedError("Sc-server takes a long time to respond")  # never uses
        return response

    def get_event(self, event_id: int) -> ScEvent | None:
        return self._events_dict.get(event_id)

    def drop_event(self, event_id: int):
        del self._events_dict[event_id]

    def set_event(self, sc_event: ScEvent) -> None:
        self._events_dict[sc_event.id] = sc_event

    def _default_reconnect_handler(self) -> None:
        pass

    def _default_error_handler(self, _: Exception) -> None:
        pass

    def _default_post_reconnect_callback(self) -> None:
        pass
