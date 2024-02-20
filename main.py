from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from keras.models import load_model
from keras.src.saving.saving_lib import io
import numpy as np
from PIL import Image, ImageOps

np.set_printoptions(suppress=True)

model = load_model('./model/keras_model.h5', compile=False)
class_names = open('./model/labels.txt', 'r').readlines()

data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
size = (224, 224)

app = FastAPI()

@app.get('/')
async def index():
    return {"status": "ok", "message": "Hello World!"}

@app.post('/scan')
async def scan_ingredient(file: Annotated[bytes, File()]):
    image = Image.open(io.BytesIO(file))
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    data[0] = normalized_image_array

    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    return {"ingredient_name": class_name}
