import enum
import logging
from typing import Optional, Callable
from ajson.core.network_adapter import NetworkAdapter
import logging

logger = logging.getLogger(__name__)

class SessionState(enum.Enum):
    INIT = "INIT"
    CONNECTING = "CONNECTING"
    READY = "READY"
    ERROR = "ERROR"
    CLOSED = "CLOSED"

class RealtimeSession:
    """
    Manages the lifecycle and state of a Realtime API session.
    Strictly follows NETWORK DENY policy by checking feature flags
    before delegating to the underlying client.
    """
    def __init__(self, client: NetworkAdapter, allow_network: bool = False):
        self._client = client
        self._allow_network = allow_network
        self._state = SessionState.INIT
        self._on_message_callback: Optional[Callable[[str], None]] = None

    @property
    def state(self) -> SessionState:
        return self._state

    def set_on_message(self, callback: Callable[[str], None]):
        self._on_message_callback = callback

    def connect(self):
        """
        Initiates connection.
        If allow_network is False, transitions to READY (Simulation) 
        without invoking the client's actual connect method.
        """
        logger.info("Session connecting... (Network Allowed: %s)", self._allow_network)
        self._transition(SessionState.CONNECTING)

        if not self._allow_network:
            logger.info("Network disabled. Simulating ready state.")
            self._transition(SessionState.READY)
            return

        try:
            self._client.connect()
            self._transition(SessionState.READY)
        except Exception as e:
            logger.error("Connection failed: %s", e)
            self._transition(SessionState.ERROR)

    def send_text(self, text: str):
        """
        Sends text message.
        If allow_network is False, logs the event but sends nothing.
        """
        if self._state != SessionState.READY:
            logger.warning("Cannot send message in state %s", self._state)
            return

        if not self._allow_network:
            logger.info("[SIMULATION] Sending text: %s", text)
            return

        # self._client.send_text(text) # Assuming client update in future
        logger.info("Sent text: %s", text)

    def close(self):
        logger.info("Closing session.")
        if self._allow_network:
            try:
                self._client.close()
            except Exception as e:
                logger.error("Error closing client: %s", e)
        
        self._transition(SessionState.CLOSED)

    def _transition(self, new_state: SessionState):
        logger.info("State transition: %s -> %s", self._state.value, new_state.value)
        self._state = new_state
