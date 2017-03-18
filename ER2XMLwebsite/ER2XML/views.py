from django.shortcuts import render, get_object_or_404, redirect
from .models import ERModel, Table, XMLSchema, Column, Constraint
from .forms import ERForm, TableForm, ColumnForm, ConstraintForm, DocumentForm, SchemaForm
from django.template import RequestContext
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import tempfile
import os

# @require_http_methods(['POST'])
def upload_model(request):
    # Handle file upload
    if request.method == 'POST':
        docform = DocumentForm(request.POST, request.FILES)
        if docform.is_valid():
            newmodel = None
            file = request.FILES['docfile']
            with tempfile.TemporaryFile() as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk.replace('\n', '<br>'))
                tmp.seek(0)
                newmodel = ERModel(name=os.path.splitext(file.name)[0],text=tmp.read())
                # newmodel.save()
            erform = ERForm(instance=newmodel)
            # return HttpResponseRedirect(reverse('upload_model'))
    else:
        docform = DocumentForm()
        erform = ERForm()
    return render(request, 'ER2XML/model_upload.html', {'docform': docform, 'erform': erform})

def schema_create(request):
    if request.method == 'POST':
        form = ERForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            return redirect('schema_edit', pk=1)
    else:
        form = ERForm()
    return render(request, 'ER2XML/upload_model.html', {'form': form})

def model_list(request):
    models = ERModel.objects.all()
    return render(request, 'ER2XML/model_list.html', {'models': models})

def model_detail(request, pk):
    model = get_object_or_404(ERModel, pk=pk)
    return render(request, 'ER2XML/model_detail.html', {'model': model})

def schema_detail(request, pk):
    schema = get_object_or_404(XMLSchema, pk=pk)
    return render(request, 'ER2XML/schema_detail.html', {'schema': schema})

def schema_edit(request, pk):
    model = get_object_or_404(ERModel, pk=pk)
    forms = {}
    for table in model.tables.all():
        items = []
        for column in table.columns.all():
            form = ColumnForm(instance=column)
            items.append(form)
        for constraint in table.constraints.all():
            form = ConstraintForm(instance=constraint)
            items.append(form)
        forms[table.name]=items
    # if form.is_valid():
    #     model = form.save(commit=False)
    #     model.save()
    if request.method == "POST":
        return redirect('schema_save', pk=model.pk)
    else:
        return render(request, 'ER2XML/schema_edit.html', {'forms': forms})

def model_edit(request, pk):
    model = get_object_or_404(ERModel, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=model)
        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            return redirect('model_detail', pk=model.pk)
    else:
        form = PostForm(instance=model)
    return render(request, 'ER2XML/model_edit.html', {'form': form})

def model_remove(request, pk):
    model = get_object_or_404(ERModel, pk=pk)
    model.delete()
    return redirect('model_list')

def schema_save(request, pk):
    schema= get_object_or_404(XMLSchema, pk=pk)
    # if request.method == "POST":
    #     form = SchemaForm(request.POST, instance=schema)
    #     if form.is_valid():
    #         schema = form.save(commit=False)
    #         schema.save()
    return redirect('schema_detail', pk=schema.pk)
    # else:
    #     form = SchemaForm(instance=schema)
    # return render(request, 'ER2XML/schema_save.html', {'form': form})