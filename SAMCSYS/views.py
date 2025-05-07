from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import json
from .models import MTTB_User, MTTB_Divisions, MTTB_Role_Master
import datetime
import hashlib
from django.middleware.csrf import get_token

# ເພີ່ມຟັງຊັນເພື່ອໃຫ້ client ສາມາດດຶງ CSRF token ໄດ້
@csrf_exempt
def get_csrf_token_view(request):
    """
    ສົ່ງ CSRF token ໃຫ້ client
    """
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

# ຟັງຊັ້ນຊ່ວຍເຫຼືອສຳລັບການແປງຂໍ້ມູນ QuerySet ເປັນ dict
def user_to_dict(user):
    """
    ແປງຂໍ້ມູນຜູ້ໃຊ້ເປັນຮູບແບບ dictionary ສຳລັບສົ່ງກັບເປັນ JSON
    """
    return {
        'id': user.id,
        'User_Id': user.User_Id,
        'User_Name': user.User_Name,
        'User_Email': user.User_Email,
        'User_Mobile': user.User_Mobile,
        'User_Status': user.User_Status,
        'Div_Id': {
            'id': user.Div_Id.id,
            'name': user.Div_Id.name if user.Div_Id else None
        } if user.Div_Id else None,
        'Role_ID': {
            'id': user.Role_ID.id,
            'name': user.Role_ID.name if user.Role_ID else None
        } if user.Role_ID else None,
        'Auth_Status': user.Auth_Status,
        'InsertDate': user.InsertDate.strftime('%Y-%m-%d %H:%M:%S') if user.InsertDate else None,
        'UpdateDate': user.UpdateDate.strftime('%Y-%m-%d %H:%M:%S') if user.UpdateDate else None,
    }

# ຟັງຊັ້ນສຳລັບການ hash ລະຫັດຜ່ານ
def hash_password(password):
    """
    ເຂົ້າລະຫັດຜ່ານດ້ວຍ SHA-256
    """
    return hashlib.sha256(password.encode()).hexdigest()

# API endpoint ສຳລັບສະແດງລາຍການຜູ້ໃຊ້
@csrf_exempt  # ເພີ່ມ csrf_exempt ເພື່ອແກ້ໄຂບັນຫາ CSRF
@require_http_methods(["GET"])
def api_user_list(request):
    """
    API ສຳລັບສະແດງລາຍການຜູ້ໃຊ້ທັງໝົດ, ສະໜັບສະໜູນການຄົ້ນຫາ ແລະ ການແບ່ງໜ້າ
    """
    try:
        # ຮັບພາລາມິເຕີຈາກ request
        search_term = request.GET.get('search', '')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # ກຳນົດການຄົ້ນຫາ
        if search_term:
            users = MTTB_User.objects.filter(
                Q(User_Id__icontains=search_term) | 
                Q(User_Name__icontains=search_term) |
                Q(User_Email__icontains=search_term) |
                Q(User_Mobile__icontains=search_term)
            )
        else:
            users = MTTB_User.objects.all()
        
        # ການແບ່ງໜ້າ
        paginator = Paginator(users, page_size)
        page_obj = paginator.get_page(page_number)
        
        # ແປງຂໍ້ມູນ
        user_list = [user_to_dict(user) for user in page_obj]
        
        # ສ້າງຂໍ້ມູນສຳລັບການແບ່ງໜ້າ
        pagination = {
            'total_items': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_number,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
        
        return JsonResponse({
            'status': 'success',
            'data': user_list,
            'pagination': pagination
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# API endpoint ສຳລັບສະແດງລາຍລະອຽດຂອງຜູ້ໃຊ້
@csrf_exempt  # ເພີ່ມ csrf_exempt ເພື່ອແກ້ໄຂບັນຫາ CSRF
@require_http_methods(["GET"])
def api_user_detail(request, user_id):
    """
    API ສຳລັບສະແດງລາຍລະອຽດຂອງຜູ້ໃຊ້ຕາມ User_Id
    """
    try:
        user = MTTB_User.objects.get(User_Id=user_id)
        return JsonResponse({
            'status': 'success',
            'data': user_to_dict(user)
        })
        
    except MTTB_User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'ບໍ່ພົບຜູ້ໃຊ້'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# API endpoint ສຳລັບເພີ່ມຜູ້ໃຊ້ໃໝ່
# ປັບປຸງຟັງຊັ້ນ api_create_user

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# ເອົາອອກຄຳສັ່ງ @require_http_methods("POST") ແລະ ອະນຸຍາດການໃຊ້ທັງ GET ແລະ POST
@csrf_exempt
def api_create_user(request):
   
    """
    API ສຳລັບເພີ່ມຜູ້ໃຊ້ໃໝ່
    """
    # ຮັບຮອງການໃຊ້ທັງ GET ແລະ POST
    if request.method == 'GET':
        return JsonResponse({
            'status': 'info',
            'message': 'ໃຊ້ method POST ເພື່ອສ້າງຜູ້ໃຊ້ໃໝ່',
            'example': {
                'User_Id': 'user123',
                'User_Name': 'ຊື່ຜູ້ໃຊ້',
                'User_Password': 'ລະຫັດຜ່ານ',
                'User_Email': 'email@example.com',
                'User_Mobile': '02012345678',
                'Div_Id': 1,
                'Role_ID': 1,
                'User_Status': True,
                'Maker_Id': 'admin001'
            }
        })
    elif request.method == 'POST':
        try:
            # ກວດວ່າຮັບຂໍ້ມູນມາໄດ້ບໍ່
            if not request.body:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ບໍ່ມີຂໍ້ມູນໃນ request body'
                }, status=400)
                
            # ຮັບຂໍ້ມູນຈາກ request
            data = json.loads(request.body)
            
            # ກວດສອບລະຫັດຜູ້ໃຊ້ຊໍ້າກັນ
            if MTTB_User.objects.filter(User_Id=data.get('User_Id')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'ລະຫັດຜູ້ໃຊ້ນີ້ມີຢູ່ໃນລະບົບແລ້ວ'
                }, status=400)
            
            # ສ່ວນທີ່ເຫຼືອຄືເດີມ...
            # ກວດສອບຂໍ້ມູນທີ່ຈຳເປັນ
            required_fields = ['User_Id', 'User_Name', 'User_Password']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'ກະລຸນາປ້ອນຂໍ້ມູນ {field}'
                    }, status=400)
            
            # ເຂົ້າລະຫັດຜ່ານ
            hashed_password = hash_password(data.get('User_Password'))
            
            # ຕັ້ງຄ່າຂໍ້ມູນພາຍນອກ (ຖ້າມີ)
            div_id = None
            if data.get('Div_Id'):
                try:
                    div_id = MTTB_Divisions.objects.get(id=data.get('Div_Id'))
                except MTTB_Divisions.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'ບໍ່ພົບຂໍ້ມູນພະແນກ'
                    }, status=400)
                    
            role_id = None
            if data.get('Role_ID'):
                try:
                    role_id = MTTB_Role_Master.objects.get(id=data.get('Role_ID'))
                except MTTB_Role_Master.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'ບໍ່ພົບຂໍ້ມູນບົດບາດ'
                    }, status=400)
            
            # ຕັ້ງຄ່າຂໍ້ມູນຜູ້ສ້າງ (ຖ້າມີ maker_id)
            maker_id = None
            if data.get('Maker_Id'):
                try:
                    maker_id = MTTB_User.objects.get(User_Id=data.get('Maker_Id'))
                except MTTB_User.DoesNotExist:
                    pass
            
            # ສ້າງຜູ້ໃຊ້ໃໝ່
            user = MTTB_User(
                User_Id=data.get('User_Id'),
                User_Name=data.get('User_Name'),
                User_Password=hashed_password,
                User_Email=data.get('User_Email'),
                User_Mobile=data.get('User_Mobile'),
                Div_Id=div_id,
                User_Status=data.get('User_Status', True),
                Maker_Id=maker_id,
                Maker_DT_Stamp=timezone.now(),
                Auth_Status='P',  # Pending
                Role_ID=role_id,
                InsertDate=timezone.now(),  # ເພີ່ມ InsertDate
            )
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'ເພີ່ມຜູ້ໃຊ້ສຳເລັດແລ້ວ',
                'data': user_to_dict(user)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'ຮູບແບບ JSON ບໍ່ຖືກຕ້ອງ'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    else:
        # ຮັບຮອງແຕ່ GET ແລະ POST ເທົ່ານັ້ນ
        return JsonResponse({
            'status': 'error',
            'message': 'Method ບໍ່ຖືກຕ້ອງ. ຮັບຮອງແຕ່ GET ແລະ POST ເທົ່ານັ້ນ'
        }, status=405)

# API endpoint ສຳລັບແກ້ໄຂຜູ້ໃຊ້
@csrf_exempt  # ໄດ້ມີ csrf_exempt ຢູ່ແລ້ວ
@require_http_methods(["PUT", "PATCH"])
def api_update_user(request, user_id):
    """
    API ສຳລັບແກ້ໄຂຂໍ້ມູນຜູ້ໃຊ້
    """
    try:
        # ຮັບຂໍ້ມູນຈາກ request
        data = json.loads(request.body)
        
        # ຄົ້ນຫາຜູ້ໃຊ້
        try:
            user = MTTB_User.objects.get(User_Id=user_id)
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ບໍ່ພົບຜູ້ໃຊ້'
            }, status=404)
        
        # ອັບເດດຂໍ້ມູນ
        if 'User_Name' in data:
            user.User_Name = data.get('User_Name')
            
        if 'User_Password' in data and data.get('User_Password'):
            user.User_Password = hash_password(data.get('User_Password'))
            
        if 'User_Email' in data:
            user.User_Email = data.get('User_Email')
            
        if 'User_Mobile' in data:
            user.User_Mobile = data.get('User_Mobile')
            
        if 'User_Status' in data:
            user.User_Status = data.get('User_Status')
            
        if 'Div_Id' in data and data.get('Div_Id'):
            try:
                user.Div_Id = MTTB_Divisions.objects.get(id=data.get('Div_Id'))
            except MTTB_Divisions.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ບໍ່ພົບຂໍ້ມູນພະແນກ'
                }, status=400)
                
        if 'Role_ID' in data and data.get('Role_ID'):
            try:
                user.Role_ID = MTTB_Role_Master.objects.get(id=data.get('Role_ID'))
            except MTTB_Role_Master.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ບໍ່ພົບຂໍ້ມູນບົດບາດ'
                }, status=400)
        
        # ຕັ້ງຄ່າຂໍ້ມູນຜູ້ແກ້ໄຂ (ຖ້າມີ checker_id)
        if 'Checker_Id' in data and data.get('Checker_Id'):
            try:
                user.Checker_Id = MTTB_User.objects.get(User_Id=data.get('Checker_Id'))
                user.Checker_DT_Stamp = timezone.now()
            except MTTB_User.DoesNotExist:
                pass
        
        # ຕັ້ງສະຖານະການອະນຸມັດ
        user.Auth_Status = 'P'  # Pending
        
        # ບັນທຶກການປ່ຽນແປງ
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'ແກ້ໄຂຂໍ້ມູນຜູ້ໃຊ້ສຳເລັດແລ້ວ',
            'data': user_to_dict(user)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'ຮູບແບບ JSON ບໍ່ຖືກຕ້ອງ'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# API endpoint ສຳລັບລົບຜູ້ໃຊ້
@csrf_exempt  # ໄດ້ມີ csrf_exempt ຢູ່ແລ້ວ
@require_http_methods(["DELETE"])
def api_delete_user(request, user_id):
    """
    API ສຳລັບລົບຜູ້ໃຊ້ (soft delete)
    """
    try:
        # ຄົ້ນຫາຜູ້ໃຊ້
        try:
            user = MTTB_User.objects.get(User_Id=user_id)
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ບໍ່ພົບຜູ້ໃຊ້'
            }, status=404)
        
        # ຮັບຂໍ້ມູນ checker_id ຖ້າມີ
        data = {}
        if request.body:
            data = json.loads(request.body)
            
        # ຕັ້ງຄ່າຂໍ້ມູນຜູ້ລົບ (ຖ້າມີ checker_id)
        if data.get('Checker_Id'):
            try:
                user.Checker_Id = MTTB_User.objects.get(User_Id=data.get('Checker_Id'))
                user.Checker_DT_Stamp = timezone.now()
            except MTTB_User.DoesNotExist:
                pass
        
        # Soft delete
        user.User_Status = False
        user.Auth_Status = 'P'  # Pending
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'ລົບຜູ້ໃຊ້ສຳເລັດແລ້ວ'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'ຮູບແບບ JSON ບໍ່ຖືກຕ້ອງ'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# API endpoint ສຳລັບການອະນຸມັດການປ່ຽນແປງຂອງຜູ້ໃຊ້
@csrf_exempt  # ໄດ້ມີ csrf_exempt ຢູ່ແລ້ວ
@require_http_methods(["POST"])
def api_approve_user(request, user_id):
    """
    API ສຳລັບອະນຸມັດການສ້າງ, ແກ້ໄຂ, ຫຼື ລົບຜູ້ໃຊ້
    """
    try:
        # ຮັບຂໍ້ມູນຈາກ request
        data = json.loads(request.body)
        
        # ກວດສອບ checker_id
        if not data.get('Checker_Id'):
            return JsonResponse({
                'status': 'error',
                'message': 'ກະລຸນາລະບຸລະຫັດຜູ້ອະນຸມັດ'
            }, status=400)
        
        # ຄົ້ນຫາຜູ້ໃຊ້
        try:
            user = MTTB_User.objects.get(User_Id=user_id)
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ບໍ່ພົບຜູ້ໃຊ້'
            }, status=404)
        
        # ຕັ້ງຄ່າຂໍ້ມູນຜູ້ອະນຸມັດ
        try:
            checker = MTTB_User.objects.get(User_Id=data.get('Checker_Id'))
            user.Checker_Id = checker
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ບໍ່ພົບຜູ້ອະນຸມັດ'
            }, status=400)
        
        # ອັບເດດສະຖານະການອະນຸມັດ
        user.Auth_Status = 'A'  # Approved
        user.Checker_DT_Stamp = timezone.now()
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'ອະນຸມັດການປ່ຽນແປງສຳເລັດແລ້ວ',
            'data': user_to_dict(user)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'ຮູບແບບ JSON ບໍ່ຖືກຕ້ອງ'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# API endpoint ສຳລັບການປະຕິເສດການປ່ຽນແປງຂອງຜູ້ໃຊ້
@csrf_exempt  # ໄດ້ມີ csrf_exempt ຢູ່ແລ້ວ
@require_http_methods(["POST"])
def api_reject_user(request, user_id):
    """
    API ສຳລັບປະຕິເສດການສ້າງ, ແກ້ໄຂ, ຫຼື ລົບຜູ້ໃຊ້
    """
    try:
        # ຮັບຂໍ້ມູນຈາກ request
        data = json.loads(request.body)
        
        # ກວດສອບ checker_id
        if not data.get('Checker_Id'):
            return JsonResponse({
                'status': 'error',
                'message': 'ກະລຸນາລະບຸລະຫັດຜູ້ປະຕິເສດ'
            }, status=400)
        
        # ຄົ້ນຫາຜູ້ໃຊ້
        try:
            user = MTTB_User.objects.get(User_Id=user_id)
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ບໍ່ພົບຜູ້ໃຊ້'
            }, status=404)
        
        # ຕັ້ງຄ່າຂໍ້ມູນຜູ້ປະຕິເສດ
        try:
            checker = MTTB_User.objects.get(User_Id=data.get('Checker_Id'))
            user.Checker_Id = checker
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ບໍ່ພົບຜູ້ປະຕິເສດ'
            }, status=400)
        
        # ອັບເດດສະຖານະການອະນຸມັດ
        user.Auth_Status = 'R'  # Rejected
        user.Checker_DT_Stamp = timezone.now()
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'ປະຕິເສດການປ່ຽນແປງສຳເລັດແລ້ວ',
            'data': user_to_dict(user)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'ຮູບແບບ JSON ບໍ່ຖືກຕ້ອງ'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# API endpoint ສຳລັບເຂົ້າສູ່ລະບົບ
@csrf_exempt  # ໄດ້ມີ csrf_exempt ຢູ່ແລ້ວ
@require_http_methods(["POST"])
def api_login(request):
    """
    API ສຳລັບກວດສອບການເຂົ້າສູ່ລະບົບ
    """
    try:
        # ຮັບຂໍ້ມູນຈາກ request
        data = json.loads(request.body)
        
        # ກວດສອບຂໍ້ມູນທີ່ຈຳເປັນ
        if not data.get('User_Id') or not data.get('User_Password'):
            return JsonResponse({
                'status': 'error',
                'message': 'ກະລຸນາປ້ອນລະຫັດຜູ້ໃຊ້ ແລະ ລະຫັດຜ່ານ'
            }, status=400)
        
        # ເຂົ້າລະຫັດຜ່ານ
        hashed_password = hash_password(data.get('User_Password'))
        
        # ກວດສອບການເຂົ້າສູ່ລະບົບ
        try:
            user = MTTB_User.objects.get(User_Id=data.get('User_Id'), User_Password=hashed_password)
            
            # ກວດສອບສະຖານະຜູ້ໃຊ້
            if not user.User_Status:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ບັນຊີຜູ້ໃຊ້ນີ້ຖືກປິດການໃຊ້ງານ'
                }, status=403)
            
            # ກວດສອບສະຖານະການອະນຸມັດ
            if user.Auth_Status != 'A':
                return JsonResponse({
                    'status': 'error',
                    'message': 'ບັນຊີຜູ້ໃຊ້ນີ້ຍັງບໍ່ໄດ້ຮັບການອະນຸມັດ'
                }, status=403)
            
            # ສ້າງຂໍ້ມູນຜູ້ໃຊ້ທີ່ຈະສົ່ງກັບ (ບໍ່ລວມລະຫັດຜ່ານ)
            user_data = user_to_dict(user)
            
            return JsonResponse({
                'status': 'success',
                'message': 'ເຂົ້າສູ່ລະບົບສຳເລັດ',
                'data': user_data
            })
            
        except MTTB_User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'ລະຫັດຜູ້ໃຊ້ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ'
            }, status=401)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'ຮູບແບບ JSON ບໍ່ຖືກຕ້ອງ'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)