import grpc
from concurrent import futures
from protos import imageservice_pb2
from protos import imageservice_pb2_grpc
from datetime import datetime

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meajor_backend.settings')
application = get_wsgi_application()

from image_manager.models import ImageModel
import logging
import io
from django.core.files.images import ImageFile
from image_manager.views import detect_and_measure
from accounts.models import User



def process_image(image_bytes, user_id):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = f'original_image_{current_date}.jpg'
        image = ImageFile(io.BytesIO(image_bytes), name=image_name)

        current_user = User.objects.get(id=user_id)

        image_model = ImageModel.objects.create(image=image, user=current_user)
        image_model.save()
        print(f"Saved image  {image_model}")
        print(f"Image itself: {image_model.image}"),

        measured_image, heights, widths = detect_and_measure(image_model.image.path)
        image_model.heights = heights
        image_model.widths = widths
        measured_image.show()

        # Convert the measured_image to bytes
        img_byte_arr = io.BytesIO()
        measured_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Save the measured_image as an ImageFile
        measured_image_name = f'measured_image_{current_date}.jpg'
        measured_image_file = ImageFile(io.BytesIO(img_byte_arr), name=measured_image_name)
        image_model.processed_image = measured_image_file
        image_model.save()
        print(f"Saved measured image  {image_model}")
        print(f"Measured image itself: {image_model.processed_image}"),

        # Open the saved image file in binary mode
        with open(image_model.processed_image.path, 'rb') as img_file:
            # Read the entire file into a bytes object
            saved_image_bytes = img_file.read()

        return saved_image_bytes, image_model.id
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



class ImageServiceServicer(imageservice_pb2_grpc.ImageServiceServicer):
    def ProcessImage(self, request, context):
        # Process the image data from the request
        processed_image, image_id = process_image(request.image, request.userid)

        

        return imageservice_pb2.ImageGrpcModel(image=processed_image, id=image_id, userid=request.userid)

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