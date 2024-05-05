from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
import json
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from Kiepe.administrator.models import *
import datetime as dt
import base64
from geopy.geocoders import Nominatim
from rest_framework.generics import ListAPIView

def reverse_geocoding(coordinates):
    while True:
        try:
            geolocator = Nominatim(user_agent="Kiepe")
            location = geolocator.reverse(coordinates)
            return location.address
        except:
            continue
        break
    return None

# Create your views here.
class CompleteKibandaProfile(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            fname = request.data.get("fname")
            lname = request.data.get("lname")
            idtype = request.data.get("idtype")
            idnumber = request.data.get("idnumber")
            brand = request.data.get("brand")
            profile = request.data.get("profile")
            cover = request.data.get("cover")
            coords = request.data.get("coords") 
            physical_address = reverse_geocoding(coords)

            print("coordinates ", coords, type(coords))
            
            user = get_user_model().objects.get(id=int(user_id))
            if hasattr(user, "kibanda"):
                kibanda = user.kibanda
                
                kibanda.first_name = fname
                kibanda.last_name = lname
                # i expect to receive coords as array... print it before try using it here
                kibanda.coordinates  = coords
                kibanda.brand_name = brand
                kibanda.aina_ya_ID = idtype
                kibanda.ID_number = idnumber
                kibanda.physical_address = physical_address

                # how to save base64 image https://stackoverflow.com/questions/51514481/typeerror-expected-str-bytes-or-os-pathlike-object-not-imagefieldfile
                if (profile != 'null' and profile != None):
                    kibanda.image = profile
                    # base64_image = base64.b64encode(profile.read())
                    # kibanda.profile_base64 = base64_image

                if (cover != 'null' and cover != None):
                    kibanda.cover_photo = cover
                    # base64_image = base64.b64encode(cover.read())
                    # kibanda.cover_photo_base64 = base64_image
                kibanda.is_active = False
                kibanda.profile_is_completed = True
                    
                kibanda.save()

                serializer = KibandaProfileSerializer(kibanda)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            elif hasattr(user, "customer"):
                # delete the user "customer" profile
                # create a new kibanda profile
                customer = user.customer
                customer.delete()

                kibanda = KibandaProfile.objects.create(
                    user=user,
                    first_name=fname,
                    last_name=lname,
                    coordinates=coords,
                    brand_name=brand,
                    aina_ya_ID=idtype,
                    ID_number=idnumber,
                    is_active=False,
                    profile_is_completed=True,
                    physical_address=physical_address,
                )

                if (profile != 'null' and profile != None):
                    kibanda.image = profile
                    # base64_image = base64.b64encode(profile.read())
                    # kibanda.profile_base64 = base64_image

                if (cover != 'null' and cover != None):
                    kibanda.cover_photo = cover
                    # base64_image = base64.b64encode(cover.read())
                    # kibanda.cover_photo_base64 = base64_image
                    

                kibanda.save()

                status_kibanda = KibandaStatus.objects.create(
                    kibanda=kibanda,
                )
                status_kibanda.save()

                serializer = KibandaProfileSerializer(kibanda)

                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
complete_kibanda_profile = CompleteKibandaProfile.as_view()


class EditDefaultMenuItem(APIView):
    def post(self, request):
        try:
            default_id = request.data.get("default_id")
            menuItemsMetadata = request.data.get("mt")
            user_id = request.data.get("user_id")
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            print('this is mt i receive ', menuItemsMetadata, type(menuItemsMetadata), menuItemsMetadata['existing'])
            defaultMenu = DefaultMenu.objects.get(id=int(default_id))
            # don't wipe all of em... we expect to get data which looks like this
            # { existing: [{id, price}], new: [{item, price}] }
            # defaultMenu.menu.clear()
            # also if menu is not required it should not be in either existing so first get all 
            # menu and see if there is not in existing u should remove it...
            existing_menu = menuItemsMetadata['existing']
            print('HEY THIS IS EXISTING MENU... ', existing_menu)
            existing_menu_parentId = []
            for menu in existing_menu:
                existing_menu_parentId.append(int(menu['id']))
            
            print('THIS ARE EXISTING MENU PARENTID ', existing_menu_parentId)
            # you we need to delte the menu item which is not found in our incoming existing mt
            for item in defaultMenu.menu.all():
                if item.menu.id not in existing_menu_parentId:
                    item.menu.delete()
                  

            # then we should change the price of all menu found in existing_menu
            print('IM TRYING TO UPDATE THE PRICE OF ITEM')
            for emenu in existing_menu:
                # its okay since we're targetting Menuitem bu here we check for administrator menu..
                parentMenu = Menu.objects.filter(id=int(emenu['id']))
                if parentMenu.count() < 1:
                    break
                parentMenu = parentMenu.last()
                print('this is the parent menu ', parentMenu)
                menuitem = None
                for mi in defaultMenu.menu.all():
                    print('MIMI NI ', mi, mi.menu.id, parentMenu.id)
                    if mi.menu.id == parentMenu.id:
                        menuitem = mi
                        break
                # we have that "menu" lets change its price..
                print("THIS IS MENU ITEM WE TARGET ", menuitem)
                menuitem.price = emenu['price']
                menuitem.save()

            # let deal with the new menu, remember new menu should be created..

            print('IM TRYING TO MANIPULATE NEW ADDED DATA')
            for item in menuItemsMetadata['new']:
                price = item["price"]
                id = item["id"]
                adminmenuitem = Menu.objects.get(id=int(id))
                menuItem = MenuItem.objects.create(
                    kibanda=kibanda,
                    menu = adminmenuitem,
                    price = price,
                )

                menuItem.save()

                defaultMenu.menu.add(menuItem)
                
            defaultMenu.save()
           
            serializer = KibandaDefaultMenuSerializer(defaultMenu)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)

edit_kibanda_default_menu = EditDefaultMenuItem.as_view()
            

class CreateDefaultMenuItem(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            menuItemsMetadata = request.data.get("mt")

            # parsed_menuItemsMetadata = json.loads(menuItemsMetadata)
            # print('menuitemsmetadaat ', menuItemsMetadata, type(menuItemsMetadata), menuItemsMetadata[0]["id"])
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda

            defaultMenu = DefaultMenu.objects.create(
                kibanda=kibanda,
            )
            defaultMenu.save()

            for item in menuItemsMetadata:
                price = item["price"]
                id = item["id"]
                adminmenuitem = Menu.objects.get(id=int(id))
                menuItem = MenuItem.objects.create(
                    kibanda=kibanda,
                    menu = adminmenuitem,
                    price = price,
                )

                menuItem.save()

                defaultMenu.menu.add(menuItem)
                
            defaultMenu.save()
            # print('HAPA NDO NAKWAMA KAKA')
            kibanda.is_default_meal_added = True
            kibanda.save()
            serializer = KibandaDefaultMenuSerializer(defaultMenu)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
create_default_menu_item = CreateDefaultMenuItem.as_view()

            
class GetDefaultKibandaMenu(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            defaultMenu = kibanda.defaultmenu
            serializer = KibandaDefaultMenuSerializer(defaultMenu)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e, " error catched")
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
get_default_kibanda_menu = GetDefaultKibandaMenu.as_view()

class UpdateKibandaStatus(APIView):
    def post(self, request):
        try:
            print("SOMEONE CALLED ME TO UPDATE KIBANDA STATUS")
            user_id = request.data.get("user_id")
            new_status = request.data.get("status")
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            kibandaStatus = kibanda.kibandastatus
            kibandaStatus.opened = new_status == "true"
            kibandaStatus.save()
            return Response({"details": "Everything is good"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
update_kibanda_status = UpdateKibandaStatus.as_view()


class IsKibandaSetTodayAvailableMenu(APIView):
    def post(self, request):
        try:
            print('IM GET CALLED....')
            user_id = request.data.get("user_id")
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            if AvailableMenu.objects.filter(kibanda=kibanda).exists():
                availablemenu = AvailableMenu.objects.get(kibanda=kibanda)
                print('thsi is date ', availablemenu.updated_at.date(), dt.date.today())
                if availablemenu.updated_at.date() == dt.date.today():
                    print('its okay we have today amenu of this length ', availablemenu.menu.count())
                    if availablemenu.menu.count() == 0:
                        return Response({"is_available": False}, status=status.HTTP_200_OK)
                    return Response({"is_available": True}, status=status.HTTP_200_OK)
                else:
                    return Response({"is_available": False}, status=status.HTTP_200_OK)
            
            else:
                return Response({"is_available": False}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)

is_menu_available_set = IsKibandaSetTodayAvailableMenu.as_view()


class SetKibandaTodayAvailableMenu(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            menuitems = request.data.get("menuitems")
            print('menuitems ', menuitems)
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            availableMenu = None
            if AvailableMenu.objects.filter(kibanda=kibanda).exists():
                availableMenu = AvailableMenu.objects.get(kibanda=kibanda)
                availableMenu.menu.clear()
                '''
                    # sio kila muda tu-create menu_item what if its available, just grab it..
                    # we only need to load the menu_items which are available in default menu
                    # since if we load all of em, we'll have to tell user to add the price of 
                    # item which is not available in default menu.. you should do this is UI
                '''
                for item in menuitems:
                    adminmenu = Menu.objects.get(id=int(item['id']))
                    menuitem = MenuItem.objects.filter(kibanda=kibanda, menu=adminmenu)
                    menuitem = menuitem.first()
                    availableMenu.menu.add(menuitem)
                availableMenu.save()
                serialize = TodayAvailableMenuSerializer(availableMenu)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
            availableMenu = AvailableMenu.objects.create(
                kibanda=kibanda,
            )
            for item in menuitems:
                adminmenu = Menu.objects.get(id=int(item['id']))
                menuitem = MenuItem.objects.filter(kibanda=kibanda, menu=adminmenu)
                '''
                    # sio kila muda tu-create menu_item what if its available, just grab it..
                    # we only need to load the menu_items which are available in default menu
                    # since if we load all of em, we'll have to tell user to add the price of 
                    # item which is not available in default menu.. you should do this is UI
                '''
                menuitem = menuitem.first()
                availableMenu.menu.add(menuitem)
               
            availableMenu.save()
            serialize = TodayAvailableMenuSerializer(availableMenu)
            return Response(serialize.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)

set_today_available_menu = SetKibandaTodayAvailableMenu.as_view()


class SetKibandaDefaultMenuAsAvailableMenu(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            user = get_user_model().objects.get(id=int(user_id))
            kibanda = user.kibanda
            defaultMenu = kibanda.defaultmenu
            availableMenu = None
            if AvailableMenu.objects.filter(kibanda=kibanda).exists():
                availableMenu = AvailableMenu.objects.get(kibanda=kibanda)
                # if there is data then in available menu then we clear em all
                availableMenu.menu.clear()
                for item in defaultMenu.menu.all():
                    availableMenu.menu.add(item)
                availableMenu.save()
                serialize = TodayAvailableMenuSerializer(availableMenu)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
            # by default this is else block
            availableMenu = AvailableMenu.objects.create(
                kibanda=kibanda,
            )
            availableMenu.save()

            for item in defaultMenu.menu.all():
                availableMenu.menu.add(item)
            availableMenu.save()
            serialize = TodayAvailableMenuSerializer(availableMenu)
            return Response(serialize.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
set_default_menu_as_available_menu = SetKibandaDefaultMenuAsAvailableMenu.as_view()

class AvailableOpenedKibandaProfiles(APIView):
    def get(self, request):
        '''
            that is shortcut i get from github copilor for reverse lookup, here i use the 
            reverse lookup to get all the kibandas which are opened, and remember kibandastatus
            is found in kibandaStatus model which have relation with kibandaProfile model
            the reverse to kibandastatus is offered by related name of "kibandastatus" here
            you should notice that he used two underscore to get the reverse lookup field
            which is "opened" in this case
        '''
        try:
            kibandas = KibandaProfile.objects.filter(kibandastatus__opened=True)
            print('vibanda ', kibandas)
            serialize = KibandaProfileSerializer(kibandas, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
opened_vibanda = AvailableOpenedKibandaProfiles.as_view()

def inifinite_filter(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    print(limit, offset)
    qs = KibandaProfile.objects.all()
    data = KibandaProfileSerializer(qs, many=True)
    data = list(data.data)
    # print(data.sort(key=lambda x:s4 x['average_ratings'], reverse=True))
    list_dict = [] 
    for item in data:
        dict_item = dict(item)
        list_dict.append(dict_item)
    
    # list_dict = list_dict[:5]
  
    sorted_data = sorted(list_dict, key=lambda x: (x['average_ratings'] if x['average_ratings'] is not None else float('-inf')), reverse=True)
    print("SORTED DATA ", len(sorted_data))

    # lets sort the data by average_rating
    # return KibandaProfile.objects.all().order_by('-kibandaratings')
    return KibandaProfile.objects.all()[int(offset): int(offset) + int(limit)]

def is_there_more_data(request):
    offset = request.GET.get('offset')
    if int(offset) > KibandaProfile.objects.all().count():
        return False
    return True

class AllVibanda(ListAPIView):
    serializer_class = KibandaProfileSerializer

    def get_queryset(self):
        qs = inifinite_filter(self.request)

        return qs
    
    def list(self, request, *args, **kwargs):
        queryset  = self.get_queryset()
        
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "data": serializer.data,
            "has_more": is_there_more_data(request),
        })

all_restaurants = AllVibanda.as_view()

class AllVibandaAPIView(APIView):
    def get(self, request):
        try:
            vibanda = reversed(KibandaProfile.objects.all())
            serialize = KibandaProfileSerializer(vibanda, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)

all_vibanda = AllVibandaAPIView.as_view()

# this give the kibanda default menu by default if there is no menu set, so this is mainly targetted  to customer
# to see menu but not the "kibanda" coz if you want to get kibanda available menu u should not mix it with default 
# menu... so here its not good to call it when we want to get available menu..
class KibandaAvailableMenuForCustomer(APIView):
    def post(self, request):
        kibanda_id = request.data.get("kibanda_id")
        kibanda = KibandaProfile.objects.get(id=int(kibanda_id))
        availableMenu = AvailableMenu.objects.filter(kibanda=kibanda)
        try:
            if availableMenu.exists():
                availableMenu = availableMenu.first()
                # check if available menu is of today
                if availableMenu.updated_at.date() == dt.date.today():
                    serialize = TodayAvailableMenuSerializer(availableMenu)
                    return Response(serialize.data, status=status.HTTP_200_OK)

                # if available menu is not of today then we clear it and add all the menu items from default menu
                availableMenu.menu.clear()
                kibanda_default_menu = kibanda.defaultmenu
                for item in kibanda_default_menu.menu.all():
                    availableMenu.menu.add(item)
                availableMenu.save()
                serialize = TodayAvailableMenuSerializer(availableMenu)
                return Response(serialize.data, status=status.HTTP_200_OK)

        
            else:
                kibanda_default_menu = kibanda.defaultmenu
                availableMenu = AvailableMenu.objects.create(
                    kibanda=kibanda,
                    set_from_default_menu=True
                )
                for item in kibanda_default_menu.menu.all():
                    availableMenu.menu.add(item)
                availableMenu.save()
                serialize = TodayAvailableMenuSerializer(availableMenu)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST)
kibanda_today_available_menu = KibandaAvailableMenuForCustomer.as_view()

# this is good to call to kibanda since its not mix the default menu if  the kibanda is not available..
class KibandaAvailableMenuOriginalAPIView(APIView):
    def post(self, request):
        kibanda_id = request.data.get("kibanda_id")
        try:
            kibanda = KibandaProfile.objects.get(id=int(kibanda_id))
            availableMenu = AvailableMenu.objects.filter(kibanda=kibanda)

            if availableMenu.exists():
                availableMenu = availableMenu.first()

                if availableMenu.updated_at.date() == dt.date.today():
                    print('I HAVE PURE AVAILABLE MENU OF TODAY SO NO NEED TO CLEAR MENU ITEMS')
                    serialize = TodayAvailableMenuSerializer(availableMenu)
                    return Response(serialize.data, status=status.HTTP_200_OK)

                # if available menu is not of today then we should clear it
                # HII NDO API INAYO-CLEAR DUH I DON'T KNOW WHY IT CLEAR ALL OF EM
                print("THIS IS AVAILABLE MENU DATE ", availableMenu.updated_at.date())
                print('THIS IS AVAILABLE MENU ', availableMenu.menu)
                print('available menu IS NOT OF TODAY SO WE SHOULD CLEAR IT')
                availableMenu.menu.clear()
                # then we should send this empty array to the user..
                serialize = TodayAvailableMenuSerializer(availableMenu)
                return Response(serialize.data, status=status.HTTP_200_OK)
            
            else:
                # it means no available menu array, which it does not make sense..
                # but for this case just return empty array..
                return Response({}, status=status.HTTP_200_OK)
        
        except Exception as err:
            return Response({"details": str(err)}, status=status.HTTP_400_BAD_REQUEST)

pure_kibanda_available_menu_no_auto_add_default_menu = KibandaAvailableMenuOriginalAPIView.as_view()


class AddOrRemoveMenuFromTodayAvailableMenu(APIView):
    def post(self, request):
        menu_id = request.data.get("menu_id")
        action = request.data.get("status")
        kibanda_id = request.data.get("kibanda_id")

        try:
            kibanda = KibandaProfile.objects.get(id=int(kibanda_id))
            availableMenu = AvailableMenu.objects.filter(kibanda=kibanda)
            if availableMenu.exists():
                availableMenu = availableMenu.first()
                menu = MenuItem.objects.get(id=int(menu_id))
                if action == "add":
                    availableMenu.menu.add(menu)
                    availableMenu.save()
                    serialize = TodayAvailableMenuSerializer(availableMenu)
                    return Response(serialize.data, status=status.HTTP_200_OK)
                elif action == "remove":
                    availableMenu.menu.remove(menu)
                    availableMenu.save()
                    serialize = TodayAvailableMenuSerializer(availableMenu)
                    return Response(serialize.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({"message": "No available menu found"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as err:
            return Response({"details": str(err)}, status=status.HTTP_400_BAD_REQUEST)

add_or_remove_menu_from_today_available_menu = AddOrRemoveMenuFromTodayAvailableMenu.as_view()


class EditKibandaProfile(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            fname = request.data.get("fname")
            lname = request.data.get("lname")
            brand = request.data.get("brand")
            profile = request.data.get("profile", None)
            cover = request.data.get("cover", None)
            coords = request.data.get("coords") 
            physical_address = reverse_geocoding(coords)
            phone = request.data.get("phone")
            user = get_user_model().objects.get(id=int(user_id))
            user.phone_number = phone
            user.save()
            if hasattr(user, "kibanda"):
                kibanda = user.kibanda

                kibanda.first_name = fname
                kibanda.last_name = lname
                kibanda.coordinates  = coords
                kibanda.brand_name = brand
                kibanda.physical_address = physical_address

                if (profile != 'null' and profile != None):
                    kibanda.image = profile

                if (cover != 'null' and cover != None):
                    kibanda.cover_photo = cover
                
                kibanda.save()

                serializer = KibandaProfileSerializer(kibanda)

                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                print("Here we edit kibanda user profile not other profile")
        
        except Exception as e:
            print(e)
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

edit_kibanda_profile = EditKibandaProfile.as_view()
