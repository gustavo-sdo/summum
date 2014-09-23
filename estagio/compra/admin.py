#-*- coding: UTF-8 -*-
from django.contrib import admin
from models import *
from forms import *


class ItensCompraInline(admin.TabularInline):
    form = ItensCompraForm
    model = ItensCompra
    can_delete = False
    extra = 3
    fields = ('produto', 'quantidade', 'valor_unitario', 'desconto', 'valor_total')
    template = "admin/compra/edit_inline/tabular.html"  # Chama o template personalizado para realizar da inline para fazer todo o tratamento necessário para a tela de compras

    # def registro(obj):
    #     if obj.pk:
    #         return True
    #     return False

    # def has_add_permission(self, request, obj=None):
    #     tem_registro = self.registro()
    #     if tem_registro:
    #         return False
    #     else:
    #         return True

    def get_formset(self, request, obj=None, **kwargs): 
        """ Altera a quantidade de inlines definida como padrão caso o registro seja salvo no BD """

        if obj: 
            kwargs['extra'] = 0 

        return super(ItensCompraInline, self).get_formset(request, obj, **kwargs) 


    def get_readonly_fields(self, request, obj=None):
        """ Define todos os campos da inline como somente leitura caso o registro seja salvo no BD """

        if obj:
            return ['produto', 'quantidade', 'valor_unitario', 'desconto', 'valor_total',]
        else:
            return []



class CompraAdmin(admin.ModelAdmin):
    inlines = [ 
        ItensCompraInline,
    ]
    form = CompraForm
    model = Compra

    search_fields = ['id', 'fornecedor']
    list_filter = ('data', 'status', 'forma_pagamento')
    readonly_fields = ('data',)

    fieldsets = (
        (None, {
            'classes': ('suit-tab suit-tab-geral',),
            'fields': ('total', 'desconto', 'status')
        }),
        (None, {
            'classes': ('suit-tab suit-tab-geral',),
            'fields': ('fornecedor', 'forma_pagamento', 'data')
        }),
        (None, {
            'classes': ('suit-tab suit-tab-info_adicionais',),
            'fields': ('observacao',)
        }),
    )

    suit_form_tabs = (
        ('geral', 'Geral'),
        ('info_adicionais', 'Informações adicionais')
    )
    
    def get_readonly_fields(self, request, obj=None):
        """ Define todos os campos da compra como somente leitura caso o registro seja salvo no BD """

        if obj:
            return ['total', 'data', 'desconto', 'fornecedor', 'forma_pagamento',]
        else:
            return ['data']


    def save_model(self, request, obj, form, change):
        if not obj.desconto:
            obj.desconto = 0

        obj.save()


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.desconto:
                instance.desconto = 0
            
            instance.save()
        formset.save_m2m()


admin.site.register(Compra, CompraAdmin)