from django.contrib import admin

from .models import (FavoriteList, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Tag, TagRecipe)

admin.site.site_header = 'Администрирование Foodgram - сайта рецептов'


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


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe',)


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    autocomplete_fields = ('tag',)


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
        TagRecipeInline,
    ]
    autocomplete_fields = ('author', 'tags',)


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
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(TagRecipe)
