import paho.mqtt.client as mqtt
from .base_handler import BaseProtocolHandler, ConnectionStatus

class MQTTHandler(BaseProtocolHandler):
    def __init__(self):
        super().__init__()
        self.client = None
        self.subscriptions = {}

    def get_config_template(self):
        return {
            "broker": "",
            "port": 1883,
            "username": "",
            "password": "",
            "use_tls": False,
            "client_id": "",
            "keep_alive": 60
        }

    async def connect(self, config):
        try:
            self.status = ConnectionStatus.CONNECTING
            self.config = config
            
            self.client = mqtt.Client(client_id=config["client_id"])
            
            if config["username"] and config["password"]:
                self.client.username_pw_set(config["username"], config["password"])
            
            if config["use_tls"]:
                self.client.tls_set()

            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            self.client.connect(
                config["broker"],
                config["port"],
                config["keep_alive"]
            )
            
            self.client.loop_start()
            self.status = ConnectionStatus.CONNECTED
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        self.status = ConnectionStatus.DISCONNECTED

    async def read_data(self, tags):
        if not self.client:
            raise ConnectionError("Not connected")
        
        results = []
        for tag in tags:
            value = self.subscriptions.get(tag["topic"])
            results.append(value)
        return results

    async def write_data(self, tags, values):
        if not self.client:
            raise ConnectionError("Not connected")
        
        results = []
        for tag, value in zip(tags, values):
            try:
                result = self.client.publish(tag["topic"], value, qos=tag.get("qos", 0))
                results.append(result.rc == mqtt.MQTT_ERR_SUCCESS)
            except Exception:
                results.append(False)
        return results

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.status = ConnectionStatus.CONNECTED
        else:
            self.status = ConnectionStatus.ERROR

    def _on_message(self, client, userdata, message):
        self.subscriptions[message.topic] = message.payload

    def _on_disconnect(self, client, userdata, rc):
        self.status = ConnectionStatus.DISCONNECTED