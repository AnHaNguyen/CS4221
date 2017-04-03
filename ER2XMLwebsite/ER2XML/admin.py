from django.contrib import admin
from .models import ERModel, Table, XMLSchema, Column, Constraint, Type, Key

admin.site.register(ERModel)
admin.site.register(Table)
admin.site.register(XMLSchema)
admin.site.register(Column)
admin.site.register(Constraint)
admin.site.register(Type)
admin.site.register(Key)