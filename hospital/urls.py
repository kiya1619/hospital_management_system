from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create-user/', views.create_user_view, name='create_user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('nurse_dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
    path('lab_dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('reception_dashboard/', views.reception_dashboard, name='reception_dashboard'),
    path('pharmacist_dashboard/', views.pharmacist_dashboard, name='pharmacist_dashboard'),

    path('user_list/', views.user_list_view, name='user_list'),
    path('delete_user/<uuid:user_id>/', views.delete_user, name='delete_user'),
    path('register_patients/', views.register_patients, name='register_patients'),
    path('schedule_appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('my_appointments/', views.my_appointments, name='my_appointments'),
    path('create_prescription/<uuid:appointment_id>/', views.create_prescription, name='create_prescription'),

    path('add_medicine/', views.add_medicine, name='add_medicine'),
    path('view_prescription/<uuid:appointment_id>', views.view_prescription, name='view_prescription'),
    path('request_lab_test/<uuid:appointment_id>/', views.request_lab_test, name='request_lab_test'),
    path('lab_requests/', views.lab_requests, name='lab_requests'),
    path('fill_lab_request/<uuid:request_id>/', views.fill_lab_request, name='fill_lab_request'),
    path('view_lab_request/<uuid:request_id>/', views.view_lab_request, name='view_lab_request'),
    path('view_lab_test/<uuid:lab_request_id>/', views.view_lab_test, name='view_lab_test'),
    path('request_bed/<uuid:appointment_id>/', views.request_bed, name='request_bed'),
    path('view_bed_request/', views.view_bed_request, name='view_bed_request'),
    path('assign_bed/<uuid:bed_request_id>/', views.assign_bed, name='assign_bed'),
    path('add_bed/', views.add_bed, name='add_bed'),
    path('medical_record/', views.view_medical_record, name='view_medical_record'),
    path('patinet_list/', views.patinet_list, name='patinet_list'),
    path('medicine_list/', views.medicine_list, name='medicine_list'),
    path('view_bedrooms/', views.view_bedrooms, name='view_bedrooms'),
    path('manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('view_appointments/', views.view_appointments, name='view_appointments'),
    path('appointments/complete/<uuid:id>/', views.complete_appointment, name='complete_appointment'),
    path('appointments/cancel/<uuid:id>/', views.cancel_appointment, name='cancel_appointment'),
    path('patient_list_nurse_view/', views.patient_list_nurse_view, name='patient_list_nurse_view'),
    path('release-bed/<uuid:bed_id>/', views.release_bed, name='release_bed'),
    path('medical-report/<uuid:appointment_id>/', views.medical_report, name='medical_report'),
    path('expired_medicine_report/', views.expired_medicine_report, name='expired_medicine_report'),

]