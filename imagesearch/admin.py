from django.contrib import admin
from .models import ProductSetInVisionAI, ProductInVisionAI, ReferrenceImagesInVisionAI
from django.http import HttpResponseRedirect

# # Register your models here.
# admin.site.register(ProductSetInVisionAI)
# admin.site.register(ProductInVisionAI)

# @admin.register(ReferrenceImagesInVisionAI)
# class ReferrenceImagesInVisionAIAdmin(admin.ModelAdmin):
#     change_form_template = "ref_image_change_form.html"
#     list_filter = ['is_registerd']

#     def response_change(self, request, obj):
#         if "_edit_bounding_polys" in request.POST:
#             return HttpResponseRedirect('/manager-admin/bounding-poly-edit/{}/'.format(obj.pk))
#         return super().response_change(request, obj)