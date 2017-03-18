from django import forms

from .models import ERModel, Table, Column, Constraint, XMLSchema

class ERForm(forms.ModelForm):

    class Meta:
        model = ERModel
        fields = ('name', 'text',)

class SchemaForm(forms.ModelForm):

    class Meta:
        model = XMLSchema
        fields = ('text',)

class TableForm(forms.ModelForm):

    class Meta:
        model = Table
        fields = ('name',)

class ColumnForm(forms.ModelForm):

    class Meta:
        model = Column
        fields = ('name','tp','minOccur','maxOccur',)

class ConstraintForm(forms.ModelForm):

    class Meta:
        model = Constraint
        fields = ('constraintType','column')

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )