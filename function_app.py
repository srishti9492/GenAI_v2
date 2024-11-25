import azure.functions as func
from process import handle_customer_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        audio_file = req.files.get("audio")
        if not audio_file:
            return func.HttpResponse("No audio file provided", status_code=400)

        response_audio = handle_customer_service(audio_file.filename)
        with open(response_audio, "rb") as f:
            return func.HttpResponse(f.read(), mimetype="audio/wav")
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
