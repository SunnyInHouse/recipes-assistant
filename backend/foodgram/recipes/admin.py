from django.contrib import admin

from .models import (FavoriteList, Ingredient, IngridientRecipe, Recipe,
                     ShoppingList, Tag)

admin.site.site_header = 'Администрирование Foodgram - сайта рецептов'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('ingridient',)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    fields = ('name', 'measurement_unit',)


class IngridientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingridient', 'recipe', 'quantity', '_quantity_unit')
    list_display_links = ('ingridient', 'recipe',)
    inline = [
        IngredientInline,
    ]

    @admin.display()
    def _quantity_unit(self, obj):
        return obj.ingridient.measurement_unit

    _quantity_unit.short_description = 'единица измерения'


class IngredientRecipeInline(admin.TabularInline):
    model = IngridientRecipe
    autocomplete_fields = ('ingridient',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', '_get_number_additions_favourite',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    inlines = [
        IngredientRecipeInline,
    ]
    autocomplete_fields = ('author', 'tags',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', )
    search_fields = ('name',)
    prepopulated_fields = {
        'slug': ('name',),
    }


class RecipeShoppingListInline(admin.StackedInline):
    model = ShoppingList.recipes.through
    extra = 1
    show_change_link = True
    verbose_name = 'Рецепт'
    verbose_name_plural = 'Рецепты в списке'


class RecipesFavouriteList(RecipeShoppingListInline):
    model = FavoriteList.recipes.through


class ShoppingListAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', )
    exclude = ('recipes',)
    inlines = [
        RecipeShoppingListInline,
    ]


class FavoriteListAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', )
    exclude = ('recipes',)
    inlines = [
        RecipesFavouriteList,
    ]


admin.site.register(FavoriteList, FavoriteListAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngridientRecipe, IngridientRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
