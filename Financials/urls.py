from django.urls import path
from . import views

urlpatterns = [
    path('create-list-financial-outcome/<str:model>/<int:object_id>/', views.FinancialOutcomeListCreateView.as_view(),
         name='create_list_financial_outcome'),
    path('update-delete-financial-outcome/<int:pk>/', views.FinancialOutcomeUpdateDeleteView.as_view(),
         name='update_delete_financial_outcome'),
    path('update-payment_method/<int:financial_id>/', views.PaymentMethodUpdateView.as_view(),
         name='update_payment_method'),

    path('list_installment_schedule/<int:installment_id>/', views.InstallmentScheduleListView.as_view(),
         name='list_installment_schedule'),
    path('update_installment_schedule/<int:pk>/', views.InstallmentScheduleUpdateView.as_view(),
         name='update_installment_schedule'),
]
