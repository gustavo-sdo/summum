#-*- coding: UTF-8 -*-
from django.db import models
from django.core.exceptions import ValidationError


class FormaPagamento(models.Model):
    nome = models.CharField(max_length=100) 
    descricao = models.CharField(max_length=250, blank=True, verbose_name=u'Descrição')
    quant_parcelas = models.IntegerField(verbose_name=u'Quantidade de parcelas') 
    prazo_entre_parcelas = models.IntegerField() 
    tipo_prazo = models.CharField(
        max_length=1, 
        blank=True,
        choices=(
            (u'D', 'Diário'),
            (u'S', 'Semanal'),
            (u'M', 'Mensal'),
        )
    ) 
    carencia = models.IntegerField(verbose_name=u'Carência')
    tipo_carencia = models.CharField(
        max_length=1, 
        blank=True, 
        verbose_name=u'Tipo de carência',
        choices=(
            (u'D', 'Diário'),
            (u'S', 'Semanal'),
            (u'M', 'Mensal'),
        )
    )
    status = models.BooleanField(default=True, help_text="Indica se a forma de pagamento está ativa para uso.")

    class Meta:
        verbose_name = u'Forma de Pagamento'
        verbose_name_plural = "Formas de Pagamento"

    def __unicode__(self):
        return u'%s' % (self.nome)


    def clean(self):
        """ Não permite que seja registrado uma forma de pagamento que tenha a quantidade de parcelas maior que 1, 
            e que o prazo entre as parcelas seja de zero. 
        """
        if self.quant_parcelas > 1 and self.prazo_entre_parcelas == 0:
            raise ValidationError('Prazo entre parcelas não pode ser 0(zero), quando a quantidade de parcelas é maior que 1(uma).')



class GrupoEncargo(models.Model):
    u""" 
        Criar classe Grupo de Encargo. Esta classe será ForeignKey numa transação financeira. 
        Isto é, numa compra, venda, geração de débito ou crédito, será possível informar o encargo que será utilizado. 
        Porém, um padrão será previamente inserido. 
    """
    TIPO_JUROS_CHOICES = (
        ('S', 'Juros Simples'),
        ('C', 'Juros Compostos'),
    )

    nome = models.CharField(max_length=100, unique=True) 
    multa = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True, verbose_name=u'Taxa de multa (%)')
    juros = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True, verbose_name=u'Taxa de juros (%)')
    tipo_juros = models.CharField(choices=TIPO_JUROS_CHOICES, max_length=1, blank=False, null=False, default='S')
    status = models.BooleanField(default=True, verbose_name=u'Ativo?')
    padrao = models.BooleanField(default=False, verbose_name=u'Padrão', help_text=u'Defini o Grupo de Encargo padrão')

    class Meta:
        verbose_name = u'Grupo de Encargo'
        verbose_name_plural = "Grupo de Encargos"

    def __unicode__(self):
        return u'%s' % (self.nome)

    def clean(self):
        """ Não permite que seja registrado uma forma de pagamento que tenha a quantidade de parcelas maior que 1, 
            e que o prazo entre as parcelas seja de zero. 
        """
        try:
            existe_padrao = GrupoEncargo.objects.filter(padrao=True).exclude(pk=self.id)
        except GrupoEncargo.DoesNotExist:
            existe_padrao = False

        if existe_padrao and self.padrao == 1:
            raise ValidationError('Já existe um grupo de encargos padrão no sistema.')

        if self.padrao == 1 and self.status == 0:
            raise ValidationError('Grupo de encargos padrão deve ser definido como ativo.')