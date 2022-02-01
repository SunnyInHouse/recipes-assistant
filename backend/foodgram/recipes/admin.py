from django.contrib import admin

from . models import Ingredient, IngridientRecipe, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('ingridient',)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    fields = ('name', 'measurement_unit',)


class IngridientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingridient', 'recipe', 'quantity', 'quantity_unit')
    list_display_links = ('ingridient', 'recipe',)
    inline = [
        IngredientInline,
    ]

    @admin.display()
    def quantity_unit(self, obj):
        return obj.ingridient.measurement_unit


class IngredientRecipeInline(admin.TabularInline):
    model = IngridientRecipe
    autocomplete_fields = ('ingridient',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags')
    inlines = [
        IngredientRecipeInline,
    ]
    autocomplete_fields = ('author',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', )
    prepopulated_fields = {
        'slug': ('name',),
    }

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngridientRecipe, IngridientRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
