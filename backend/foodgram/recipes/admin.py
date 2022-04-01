from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    search_help_text = 'поиск по ингридиентам'


class IngredientInline(admin.TabularInline):
    model = Ingredient
    fields = ('name', 'measurement_unit',)


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'quantity', '_quantity_unit')
    list_display_links = ('ingredient', 'recipe',)
    inline = [
        IngredientInline,
    ]

    @admin.display()
    def _quantity_unit(self, obj):
        return obj.ingredient.measurement_unit

    _quantity_unit.short_description = 'единица измерения'


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    autocomplete_fields = ('ingredient',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', )
    search_fields = ('name',)
    prepopulated_fields = {
        'slug': ('name',),
    }


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        '_get_number_additions_to_favourite',
        '_get_number_ingredients',
        )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    inlines = [
        IngredientInRecipeInline,
    ]
    autocomplete_fields = ('author', 'tags',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
