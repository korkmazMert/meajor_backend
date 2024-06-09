import grpc
from concurrent import futures
from protos import imageservice_pb2
from protos import imageservice_pb2_grpc

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meajor_backend.settings')
application = get_wsgi_application()

from image_manager.models import ImageModel
import sqlite3
import logging
from django.core.files.base import ContentFile



def process_image(image_bytes):
    ## Save the image to the database
    image_file = ContentFile(image_bytes)
    image_model = ImageModel.objects.create(image=image_file)
    image_model.save()

    return image_bytes

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