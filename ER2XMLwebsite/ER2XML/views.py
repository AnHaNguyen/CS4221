from django.shortcuts import render, get_object_or_404, redirect
from .models import ERModel, Table, XMLSchema, Column, Constraint, Type, ConstraintType
from .forms import ERForm, TableForm, ColumnForm, ConstraintForm, DocumentForm, SchemaForm, TypeForm
from django.template import RequestContext
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from sets import Set
from django.contrib import messages

from .RelationalXMLSchema import generateXMLSchema, generateNestedXMLSchema
from .Logic import parseXMLString, exportXMLToFile
import tempfile
import os

tp_choices=["xs:string","xs:date","xs:decimal","xs:boolean","xs:integer"]
selected_types=[]

def upload_model(request):
    # Handle file upload
    # print(tp_choices)
    # print(selected_types)
    if request.method == 'POST':
        docform = DocumentForm(request.POST, request.FILES)
        if docform.is_valid():
            newmodel = None
            file = request.FILES['docfile']
            with tempfile.TemporaryFile() as tmp:
                for chunk in file.chunks():
                    # tmp.write(chunk.replace('\n',''))
                    tmp.write(chunk)
                tmp.seek(0)
                newmodel = ERModel(name=os.path.splitext(file.name)[0],text=tmp.read())
            erform = ERForm(instance=newmodel)
        else:
            erform = ERForm()
    else:
        docform = DocumentForm()
        erform = ERForm()
    return render(request, 'ER2XML/model_upload.html', {'docform': docform, 'erform': erform})

def column_update(request,pk):
    form = ColumnForm(request.POST)
    if form.is_valid():
        form.save()
    print(form)
    # return redirect('schema_edit', pk=pk)

def schema_create(request):
    if request.method == 'POST':
        form = ERForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            tables = parseXMLString(model)
            return redirect('schema_edit', pk=model.pk)
    else:
        form = ERForm()
    return render(request, 'ER2XML/upload_model.html', {'form': form})

def schema_detail(request, pk):
    # select plain, nested, or DTD
    # export the selected
    # if nested, select order
    model = get_object_or_404(ERModel, pk=pk)
    if request.POST:
        if 'Export' in request.POST:
            choice='Nested'
            form = SchemaForm(request.POST)
            if form.is_valid():
                exportXMLToFile(model.name+'_schema.xsd', str(form.instance.text))
                messages.info(request, 'The schema has been exported to '+model.name+'_schema.xsd')
        elif 'Nested' in request.POST:
            choice = 'Nested'
            tables = model.tables.all()
            form = SchemaForm(initial={'text':generateNestedXMLSchema(model,[tables[0]])})
        elif 'setOrder' in request.POST:
            choice = 'Nested'
            tables = model.tables.all()
            # tableIDs = request.POST.getlist['rootElement']
            # tableID = tableIDs[0]
            # tables=model.tables.filter(tableId=tableID)
            # print(table)
            form = SchemaForm(initial={'text':generateNestedXMLSchema(model,[tables[2]])})
        else:        
            choice = 'Plain'
            form = SchemaForm(initial={'text':generateXMLSchema(model)})
    else:
        choice = 'Plain'
        form = SchemaForm(initial={'text':generateXMLSchema(model)})
    return render(request, 'ER2XML/schema_detail.html', {'name':model.name, 'form': form, 'choice':choice, 'pk':pk})

def schema_edit(request,pk):
    model = get_object_or_404(ERModel, pk=pk)
    forms = {}
    candikeys = {}
    fts = {}
    for table in model.tables.all():
        items = []
        keys = []
        ts = []
        for column in table.columns.all():
            isFK = False
            for constr in column.constr.all():
                if constr.constraintType == ConstraintType.FOREIGN_KEY:
                    refTable = Table.objects.filter(model=model,tableId=constr.referredTable)
                    ts.append(refTable[0].name)
                    isFK = True
            if not isFK:
                form = ColumnForm(tp_choices=tp_choices,instance=column)
                items.append(form)
        forms[table.name]=items
        fts[table.name]=list(Set(ts))
        for key in table.keys.all():
            keys.append(key)
        candikeys[table.name]=keys
    return render(request, 'ER2XML/schema_edit.html', {'forms': forms, 'candikeys': candikeys, 'fts': fts, 'pk': model.pk})

def schema_save(request, pk):
    model = get_object_or_404(ERModel, pk=pk)
    if request.method == "POST":
        tables = model.tables.all()
        re = []
        re.append(tables[0])
    # else:
    #     form = SchemaForm(instance=schema)
    # return render(request, 'ER2XML/schema_save.html', {'form': form})
    # update domain
    # update primary key
    # Update the not null, primary key, and foreign key to min_occur
    # unique, foreign key, and primary key appear as constraints

        pks=request.POST.getlist('primarykey')
        print(pks)
        # newpks=[]
        # for primekey in pks:
        #     if primekey.is_valid():
        #         for key in primekey.colIds:
        #             newpks.append[key]
        #         columns=primekey.table.columns.all()
        #         for column in columns:
        #             for constr in colume.constr.all():
        #                 if constr.constraintType == ConstraintType.PRIMARY_KEY and 

        # for i, form in enumerate(cols):
        #     if form.is_valid():
        #         tables[i]=form.save(commit=False)            
        #         if form.field_exists('UNIQUE'):
        #             print(form.fields('UNIQUE'))
                    # tables[i]
        xmlString = generateXMLSchema(model)
        # xmlString = generateNestedXMLSchema(model)
        schema= XMLSchema(model=model,text=xmlString)
        schema.save()
        return redirect('schema_detail', pk=model.pk)
    else:
        return redirect('schema_edit', pk=model.pk)

def type_add(request):
    if request.method == "POST":
        form = TypeForm(request.POST)
        if form.is_valid():
            customType = form.save(commit=False)
            customType.save()
            return redirect('type_detail', pk=customType.pk)
    else:
        form = TypeForm()
    return render(request, 'ER2XML/type_edit.html', {'form': form})

def type_edit(request, pk):
    customType = get_object_or_404(Type, pk=pk)
    
    if request.method == "POST":
        form = TypeForm(request.POST, instance=customType)
        if form.is_valid():
            customType = form.save(commit=False)
            customType.save()
            return redirect('type_detail', pk=customType.pk)
    else:
        form = TypeForm(instance=customType)
    return render(request, 'ER2XML/type_edit.html', {'form': form, 'pk': pk})

def type_remove(request, pk):
    customType = get_object_or_404(Type, pk=pk)
    customType.delete()
    return redirect('type_list')

def type_set(request):
    if 'typeSet' in request.POST:
        selected=request.POST.getlist('selected')
        print(selected)
        for item in selected:
            if item not in selected_types:
                customType = get_object_or_404(Type, pk=item)
                selected_types.append(item)
                tp_choices.append(customType.text)
    elif 'typeReset' in request.POST:
        tp_choices[:]=["xs:string","xs:date","xs:decimal","xs:boolean","xs:integer"]
        selected_types[:]=[]
    return redirect('upload_model')

def type_list(request):
    types = Type.objects.all()
    enumTypes = {str(i+1):item for i, item in enumerate(types)}
    return render(request, 'ER2XML/type_list.html', {'enumTypes': enumTypes.iteritems(), 'selected': selected_types})

def type_detail(request, pk):
    customType = get_object_or_404(Type, pk=pk)
    return render(request, 'ER2XML/type_detail.html', {'customType': customType})