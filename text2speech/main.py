import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
from flask import Flask, request, send_file
from flask_cors import CORS
import sys
from tempfile import gettempdir

polly = boto3.client('polly')

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    data = request.args
    if data.get('language') == 'null':
        
        try:
            response = polly.synthesize_speech(Text=data.get('text'),
                                            OutputFormat="mp3", VoiceId=data.get('voice'))
        except (BotoCoreError, ClientError) as error:
            print(error)
            sys.exit(-1)

        if "AudioStream" in response:
                with closing(response["AudioStream"]) as stream:
                    output = os.path.join(gettempdir(), "speech.mp3")
                    try:
                        with open(output, "wb") as file:
                            file.write(stream.read())
                    except IOError as error:
                        print(error)
                        sys.exit(-1)
        else:
            print("Could not stream audio")
            sys.exit(-1)

        return send_file(output, as_attachment=True)
    else:
        response = polly.describe_voices(LanguageCode=data.get('language'))
        return response

if __name__ == '__main__':
    app.run(debug=True, port=4500)
