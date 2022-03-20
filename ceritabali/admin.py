from django.contrib import admin
from .models import TF, Document, Filter, Term

# Register your models here.
admin.site.register(Document)
admin.site.register(Term)
admin.site.register(TF)
admin.site.register(Filter)
