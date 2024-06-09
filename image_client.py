import grpc
from protos import imageservice_pb2
from protos import imageservice_pb2_grpc


## to test besides mobile app
def process_image(image_path):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = imageservice_pb2_grpc.ImageServiceStub(channel)
        response = stub.ProcessImage(imageservice_pb2.ImageGrpcModel(image=image_bytes))

        # Save the image data from the response to a file
        with open('processed_image.jpg', 'wb') as f:
            f.write(response.image)

if __name__ == '__main__':
    process_image(r'D:\a.jpg')