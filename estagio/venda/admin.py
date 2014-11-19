#-*- coding: UTF-8 -*-
from django.contrib import admin
from models import *
from forms import *
from django.http import HttpResponseRedirect


class ItensVendaInline(admin.TabularInline):
    form = ItensVendaForm
    formset = ItensVendaFormSet
    model = ItensVenda
    can_delete = False
    extra = 3
    fields = ('produto', 'quantidade', 'valor_unitario', 'desconto', 'valor_total')
    template = "admin/venda/edit_inline/tabular.html"  # Chama o template personalizado para realizar da inline para fazer todo o tratamento necessário para a tela de vendas


    def get_formset(self, request, obj=None, **kwargs): 
        u""" Altera a quantidade de inlines definida como padrão caso o registro seja salvo no BD """

        if obj: 
            kwargs['extra'] = 0 

        return super(ItensVendaInline, self).get_formset(request, obj, **kwargs) 


    def get_readonly_fields(self, request, obj=None):
        u""" Define todos os campos da inline como somente leitura caso o registro seja salvo no BD """

        if obj:
            return ['produto', 'quantidade', 'valor_unitario', 'desconto', 'valor_total',]
        else:
            return []



class VendaAdmin(admin.ModelAdmin):
    inlines = [ 
        ItensVendaInline,
    ]
    form = VendaForm
    model = Venda
    actions = None

    list_display = ('id', 'data', 'total', 'status')
    search_fields = ['id', 'cliente']
    list_filter = ('data', 'status', 'forma_pagamento', 'cliente')
    readonly_fields = ('data',)

    fieldsets = (
        (None, {
            'classes': ('suit-tab suit-tab-geral',),
            'fields': ('total', 'desconto', 'status')
        }),
        (None, {
            'classes': ('suit-tab suit-tab-geral',),
            'fields': ('cliente', 'forma_pagamento', 'data')
        }),
        (None, {
            'classes': ('suit-tab suit-tab-info_adicionais',),
            'fields': ('observacao', 'pedido', 'status_pedido',)
        }),
    )

    suit_form_tabs = (
        ('geral', 'Geral'),
        ('info_adicionais', 'Informações adicionais')
    )

    def has_delete_permission(self, request, obj=None):
        u""" Somente o usuário admin pode deletar uma venda. """
        if request.user.is_superuser:
            return True

        else:
            return False

    
    def get_readonly_fields(self, request, obj=None):
        u""" Define todos os campos da venda como somente leitura caso o registro seja salvo no BD """

        if obj:
            return ['total', 'data', 'desconto', 'cliente', 'forma_pagamento', 'pedido', 'status_pedido',]
        else:
            return ['data', 'pedido', 'status_pedido']


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


    def response_add(self, request, obj):
        u""" Trata a adição da venda dependendo do botão clicado ao salvá-la 
             Criada em 18/11/2014.
        """

        if '_addpedido' in request.POST:
            obj.pedido = 'S'
            obj.save()
            return HttpResponseRedirect("../%s" % (obj.pk))
        else:
            obj.pedido = 'N'
            obj.save()
            return super(VendaAdmin, self).response_add(request, obj)


    def response_change(self, request, obj):
        u""" Trata a alteração da venda dependendo do botão clicado ao salvá-la 
             Criada em 18/11/2014.
        """

        if '_addconfirmapedido' in request.POST:
            obj.status_pedido = True
            obj.status = False
            obj.save()
            return HttpResponseRedirect("../%s" % (obj.pk))
        else:
            return super(VendaAdmin, self).response_change(request, obj)


admin.site.register(Venda, VendaAdmin)