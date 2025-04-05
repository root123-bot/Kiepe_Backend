from rest_framework import status
from .serializers import MenuSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Menu

class MenuAPIView(APIView):
    def get(self, request):
        try:
            menus = Menu.objects.all()
            serializer = MenuSerializer(menus, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("THIS IS ERROR I'VE GOT IN RETRIEVING MENU")
            print(e)
            return Response({
                "message": "Error retrieving menus"
            }, status=status.HTTP_400_BAD_REQUEST)
        
menu_added_by_administrator = MenuAPIView.as_view()