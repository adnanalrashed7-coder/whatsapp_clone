from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import UserProfile

@login_required
def user_profile(request):
    """صفحة الملف الشخصي للمستخدم"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.display_name = request.POST.get('display_name', '')
        profile.status = request.POST.get('status', 'online')
        profile.theme = request.POST.get('theme', 'light')
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'تم تحديث الملف الشخصي')
        return redirect('chat:user_profile')
    
    return render(request, 'chat/user_profile.html', {'profile': profile})