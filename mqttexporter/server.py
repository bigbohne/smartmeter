from quart import Quart

def create_app(storage):
    app = Quart("mqttexporter")

    @app.get('/metrics')
    def metrics():
        return "\n".join(map(lambda m: str(m), storage.get_metrics()))
    
    return app