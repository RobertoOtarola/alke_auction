from .models import Category

def categorias_nav(request):
    return {'categorias_nav': Category.objects.all()}
