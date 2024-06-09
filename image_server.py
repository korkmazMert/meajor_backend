import grpc
from concurrent import futures
from protos import imageservice_pb2
from protos import imageservice_pb2_grpc
import datetime

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meajor_backend.settings')
application = get_wsgi_application()

from image_manager.models import ImageModel
import sqlite3
import logging
from django.core.files.base import ContentFile
import io
from PIL import Image
from django.core.files.images import ImageFile



def process_image(image_bytes):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = f'size_measured_image_{current_date}.jpg'
        image = ImageFile(io.BytesIO(image_bytes), name=image_name)
        image_model = ImageModel.objects.create(image=image)
        image_model.save()
        print(f"Saved image  {image_model}")
        print(f"Image itself: {image_model.image}"),

        #open the saved image
        open_image = Image.open(image_model.image)
        open_image.show()

            # Open the saved image file in binary mode
        with open(image_model.image.path, 'rb') as img_file:
            # Read the entire file into a bytes object
            saved_image_bytes = img_file.read()


        return saved_image_bytes
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


class ImageServiceServicer(imageservice_pb2_grpc.ImageServiceServicer):
    def ProcessImage(self, request, context):
        # Process the image data from the request
        processed_image = process_image(request.image)

        

        return imageservice_pb2.ImageGrpcModel(image=processed_image)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    imageservice_pb2_grpc.add_ImageServiceServicer_to_server(ImageServiceServicer(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info(f"Starting server on {listen_addr}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()