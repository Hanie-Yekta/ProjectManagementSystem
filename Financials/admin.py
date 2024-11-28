from django.contrib import admin
from .models import FinancialOutcomeRecord, CashPaymentRecord, CheckPaymentRecord, InstallmentSchedule, \
    InstallmentPaymentRecord


class FinancialOutcomeRecordAdmin(admin.ModelAdmin):
    """
    manage financial outcome instances in admin panel.
    Provides additional display, filtering, and searching options
    search by -> created_by, payment_method
    filter by -> status, payment_method
    also show its create date in readonly fields
    """

    list_display = ('title', 'created_by', 'price', 'status')
    search_fields = ('created_by', 'payment_method')
    list_filter = ('status', 'payment_method')
    readonly_fields = ('create_date',)


admin.site.register(FinancialOutcomeRecord, FinancialOutcomeRecordAdmin)


class CashPaymentRecordAdmin(admin.ModelAdmin):
    """
    manage cash payment instances in admin panel.
    Provides additional display, filtering, and searching options
    search by -> it's financial outcome's title
    filter by -> status
    also show its update date in readonly fields
    """

    list_display = ('financial_outcome__title', 'payment_date', 'status')
    search_fields = ('financial_outcome__title',)
    list_filter = ('status',)
    readonly_fields = ('update_date',)


admin.site.register(CashPaymentRecord, CashPaymentRecordAdmin)


class CheckPaymentRecordAdmin(admin.ModelAdmin):
    """
    manage check payment instances in admin panel.
    Provides additional display, filtering, and searching options
    search by -> it's financial outcome's title
    filter by -> status
    also show its update date in readonly fields
    """
    list_display = ('financial_outcome__title', 'check_date', 'status')
    search_fields = ('financial_outcome__title',)
    list_filter = ('status',)
    readonly_fields = ('update_date',)


admin.site.register(CheckPaymentRecord, CheckPaymentRecordAdmin)


class InstallmentScheduleInline(admin.TabularInline):
    """
    manage inline configuration within 'InstallmentPaymentRecordAdmin''s instances in admin panel.
    """
    model = InstallmentSchedule
    fields = ('date', 'installment_status')
    can_delete = True


class InstallmentPaymentRecordAdmin(admin.ModelAdmin):
    """
    manage installment payment instances in admin panel.
    Provides additional display, filtering, and searching options
    show its update date in readonly fields
    """
    list_display = ('financial_outcome__title', 'status')
    inlines = (InstallmentScheduleInline,)
    readonly_fields = ('update_date',)


admin.site.register(InstallmentPaymentRecord, InstallmentPaymentRecordAdmin)
