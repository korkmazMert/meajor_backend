from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from .serializers import *
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO
from PIL import Image

import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from django.core.files.base import ContentFile
from PIL import Image as PilImage
from io import BytesIO
from .models import ImageModel  # Assuming ImageModel is in the same directory
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO
from PIL import Image,ImageDraw, ImageFont
import io
from datetime import datetime
from django.core.files.images import ImageFile
from accounts.models import User    
from django.core.files.uploadedfile import InMemoryUploadedFile

def detect_and_measure(image_path):
    widths_cm = []
    heights_cm = []

    # Load a pre-trained YOLOv8 model
    model = YOLO('yolov8n.pt')  # use your existing model

    # Open the image
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Make predictions
    results = model.predict(img, save=True, imgsz=640*2, conf=0.1)

    # Extract bounding box dimensions
    boxes = results[0].boxes.xywh.cpu()

    # Define the known dimensions of the credit card in cm
    card_width_cm = 8.00  # replace with actual width
    card_height_cm = 4.75  # replace with actual height

    # Find the bounding box of the credit card in the image
    min_distance = np.inf
    credit_card_box = None

    for box in boxes:
        x, y, w, h = box

        # Calculate the distance from the bottom left corner to the center of the box
        distance = np.sqrt((x - 0)**2 + (y - img_height)**2)

        # If this box is closer to the bottom left corner than the current closest box, update the closest box and the minimum distance
        if distance < min_distance:
            min_distance = distance
            credit_card_box = box

    credit_card_width_px, credit_card_height_px = credit_card_box[2], credit_card_box[3]

    # Calculate the scale of pixels to cm
    scale_width = credit_card_width_px / card_width_cm
    scale_height = credit_card_height_px / card_height_cm

    # Draw the bounding boxes on the image
    draw = ImageDraw.Draw(img)

    # Load a font (this will depend on your system)
    font = ImageFont.truetype("arial.ttf", 15)  # replace with the path to a font file on your system

    for box in boxes:
        x, y, w, h = box

        # Convert width and height from pixels to centimeters
        w_cm = round((w / scale_width).item(), 2)
        h_cm = round((h / scale_height).item(), 2)

        widths_cm.append(w_cm)
        heights_cm.append(h_cm)

        print("Width of Box: {} cm, Height of Box: {} cm".format(w_cm, h_cm))

        # Draw the rectangle on the image
        draw.rectangle([(x-w/2, y-h/2), (x+w/2, y+h/2)], outline='red')

        # Draw the text on the image
        draw.text((x-w/2, y-h/2 - 40), f'W: {w_cm} cm\nH: {h_cm} cm', fill='red', font=font)
    return img, widths_cm, heights_cm

def get_images(self):
    images = ImageModel.objects.all()
    images_serialized = ImageSerializer(images, many=True).data
    return JsonResponse({'images': images_serialized})


def get_image(self, image_id):
    image = ImageModel.objects.get(id=image_id)
    image_serialized = ImageSerializer(image).data
    return JsonResponse({'image': image_serialized})


def get_users_images(request):
    user_id = request.user.id
    images = ImageModel.objects.filter(user_id=user_id)
    images_serialized = ImageSerializer(images, many=True).data
    return JsonResponse({'images_length':len(images),'images': images_serialized,})



def save_image_to_db(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        user_id = request.user.id
        if image is None:
            return JsonResponse({'message': 'No image file received'}, status=400)

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = f'original_image_{current_date}.jpg'
        # # Convert the uploaded file to bytes
        # image_bytes = image.file.read()
        # image = ImageFile(io.BytesIO(image_bytes), name=image_name)

        current_user = User.objects.get(id=user_id)

        image_model = ImageModel.objects.create(image=image, user=current_user)
        image_model.save()



        # Process the image and get the id of the saved image model
        try:
            print(f"Image path: {image_model.image.path}")
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

        except Exception as e:
            print(f"Error in detect_and_measure: {e}")
            return JsonResponse({'message': str(e)}, status=400)


        image_model_serialized = ImageSerializer(image_model).data

        return JsonResponse({
            'result': 'success',
            'message': 'Image saved successfully',
            'image': image_model_serialized,
            })
    return JsonResponse({'message': 'Invalid request method'}, status=405)


