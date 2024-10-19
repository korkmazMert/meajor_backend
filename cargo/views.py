from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
import googlemaps
from image_manager.models import ImageModel
from image_manager.serializers import ImageSerializer


def calculate_cargo_cost(height, width, weight, from_where, to_where):
    currency = "TL"
    base_cost = 10  # base cost for sending a cargo.
    if weight is not None:
        size_cost = height * width * 0.05 * (weight * 0.1) # cost based on the size of the cargo
    else:
        size_cost = height * width * 0.05
    distance =  get_distance(from_where, to_where) #returns the distance for birds view
    distance_cost = distance * 0.1  # cost based on the distance

    total_cost = base_cost + size_cost + distance_cost
    return total_cost


# returns the birds view kilometers between two locations
def get_distance(from_where, to_where):
    geolocator = Nominatim(user_agent="cargoGeocoder")

    location1 = geolocator.geocode(from_where)
    location2 = geolocator.geocode(to_where)

    point1 = (location1.latitude, location1.longitude)
    point2 = (location2.latitude, location2.longitude)
    kilometers = geodesic(point1, point2).kilometers 
    print('kilometers',kilometers)

    return kilometers
# returns the driving distance between two locations
def get_driving_distance(from_where, to_where):
    gmaps = googlemaps.Client(key='YOUR_GOOGLE_MAPS_API_KEY')

    # Request directions
    directions_result = gmaps.directions(from_where, to_where)

    # The distance is in the first leg of the first route
    driving_distance = directions_result[0]['legs'][0]['distance']['text']

    print('Driving distance:', driving_distance)

    return driving_distance
class UpdateCargoCost(APIView):
    def post(self,request):
        from_where = request.POST.get('from_where')
        to_where = request.POST.get('to_where')
        image_id = request.POST.get('image_id')
        if not from_where or not to_where:
            return Response({'result':'failed','message': 'Please provide from_where and to_where'}, status=status.HTTP_400_BAD_REQUEST)
        image = ImageModel.objects.get(id=image_id)
        if image.selected_height == None or image.selected_width == None:
            return Response({'result':'failed','message': 'image file doesnt have height or width'}, status=status.HTTP_400_BAD_REQUEST)
        total_cost = calculate_cargo_cost(image.selected_height, image.selected_width, image.weight, from_where, to_where)
        image.total_cost = total_cost
        image.to_where = to_where
        image.from_where = from_where
        image.save()
        serialized_image = ImageSerializer(image).data
        return Response({'result':'success','message':'calculating cost success','total_cost': total_cost,'image_model':serialized_image}, status=status.HTTP_200_OK)
    
    
class GetCargoCost(APIView):
    def post(self, request):
        height = request.POST.get('height')
        width = request.POST.get('width')
        weight = request.POST.get('weight')
        from_where = request.POST.get('from_where')
        to_where = request.POST.get('to_where')
        image_id = request.POST.get('image_id')

        if not height or not width or not weight or not from_where or not to_where:
            return Response({'result':'failed','message': 'Please provide height, width, from_where and to_where'}, status=status.HTTP_400_BAD_REQUEST)
        image = ImageModel.objects.get(id=image_id)

        height = float(height)
        width = float(width)
        weight = float(weight)
       
        total_cost = calculate_cargo_cost(height, width,weight, from_where, to_where)
        # print('total_cost',json.loads(total_cost.content))

        image.total_cost = total_cost
        image.to_where = to_where
        image.from_where = from_where
        image.selected_height = height
        image.selected_width = width
        image.weight = weight
        image.save()
        serialized_image = ImageSerializer(image).data
        return Response({'result':'success','message':'calculating cost success','total_cost': total_cost,'image_model':serialized_image}, status=status.HTTP_200_OK)