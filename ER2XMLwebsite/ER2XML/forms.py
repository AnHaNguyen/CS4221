from django import forms

from .models import ERModel, Table, Column, Constraint, XMLSchema, Type, ConstraintType

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
        fields = ('name','tp',)

    UNIQUE = forms.BooleanField(required=False,initial=False)
    NOTNULL = forms.BooleanField(required=False,initial=False)

    def __init__(self, *args, **kwargs):
        tp_choices=kwargs.pop('tp_choices',None)
        super(ColumnForm, self).__init__(*args, **kwargs)  
        if tp_choices:   
            self.fields['tp'].widget = forms.Select(choices=[(tp,tp) for tp in tp_choices])
        if hasattr(self, 'instance'):
            for item in self.instance.constr.all():
                if item.constraintType == ConstraintType.NOT_NULL or item.constraintType == ConstraintType.FOREIGN_KEY:
                    del self.fields['NOTNULL']
                else:
                    del self.fields['UNIQUE']
                    del self.fields['NOTNULL']

    def save(self, commit=True):
        # do something with self.cleaned_data['temp_id']
        return super(ColumnForm, self).save(commit=commit)

class ConstraintForm(forms.ModelForm):

    class Meta:
        model = Constraint
        fields = ('column',)

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )

class TypeForm(forms.ModelForm):

    class Meta:
        model = Type
        fields = ('name','text','content',)