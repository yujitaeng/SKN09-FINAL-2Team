from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from app.views import pswd_views, signup_views, chat_views, mypage_views, recommend_views, user_views

urlpatterns = [
    path('', chat_views.chat, name='chat'),

    path('login/', user_views.login_view, name='login'),
    path('logout/', user_views.logout_view, name='logout'),
    path('pswd/', pswd_views.pswd, name='pswd'), 
    path('pswd/verif/', pswd_views.pswd_verif, name='pswd_verif'),
    
    path("api/pswd_request/", pswd_views.password_reset_request, name="password_reset_request"),
    path("api/resend_code/", pswd_views.resend_verification_code, name="resend_code"),
    path("api/verify_code/", pswd_views.verify_code, name="verify_code"),
    path("pswd/gen/", pswd_views.pswd_gen, name="pswd_gen"),
    path("api/set_password/", pswd_views.set_new_password, name="set_password"),
    path("api/check_password/", mypage_views.password_check, name="check_password"),
    
    path('birth/', user_views.birth, name='birth'),
    path('birth/recommend-products/', user_views.birth_recommend_products, name='birth_recommend_products'),
    
    path('chat/', chat_views.chat, name='chat'),
    path('chat/<int:chat_id>/', chat_views.chat_detail, name='chat_detail'),
    path('chat/guest-start/', chat_views.chat_guest_start, name='chat_guest_start'),
    
    path('mypage/', mypage_views.home, name='mypage'),
    path('mypage/profile/', mypage_views.profile_info, name='profile_info'),
    path('mypage/profile/password/', mypage_views.profile_password, name='profile_password'),
    path('mypage/profile/password/confirm', mypage_views.profile_password_confirm, name='profile_password_confirm'),
    path('mypage/profile/delete/', mypage_views.profile_delete, name='profile_delete'),
    path('mypage/profile/delete/confirm/', mypage_views.profile_delete_confirm, name='profile_delete_confirm'),
    path("api/profile/delete/", mypage_views.delete_user_account, name="delete_user_account"),
    path('mypage/profile/delete/confirm', mypage_views.profile_delete_confirm, name='profile_delete_confirm'),
    
    path('signup/step1/', signup_views.signup_step1, name='signup_step1'),
    path('signup/step2/', signup_views.signup_step2, name='signup_step2'),
    path('signup/step3/', signup_views.signup_step3, name='signup_step3'),
    path('signup/step4/', signup_views.signup_step4, name='signup_step4'),
    path('signup/step5/', signup_views.signup_step5, name='signup_step5'),
    path('signup/send-code/', signup_views.send_verification_code, name='send_verification_code'),
    path('signup/verify-code/', signup_views.verify_code, name='verify_code'),
    path('signup/check-dup/', signup_views.check_duplicate, name='check_duplicate'),
    
    path('accounts/', include('allauth.urls')),
    path('social/redirect/', signup_views.social_redirect_view, name='social_redirect'),

    path('chat/start/', chat_views.chat_start, name='chat_start'),
    path('chat/message/', chat_views.chat_message, name='chat_message'),
    path('chat/history/', chat_views.chat_history, name='chat_history'),
    path('chat/upload/', chat_views.chat_upload, name='chat_upload'),
    path('chat/feedback/<int:msg_id>', chat_views.chat_feedback, name='chat_feedback'),
    
    path('recommends', recommend_views.index, name='recommends'),
    path('recommends/<int:recommend_id>/like', recommend_views.like, name='recommend_like'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
