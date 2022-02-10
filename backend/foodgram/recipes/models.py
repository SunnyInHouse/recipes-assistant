from django.conf import settings
from django.core import validators
from django.db import models


class Ingredient(models.Model):
    """
    Модель для описания ингридиентов, входящих в рецепты.
    """

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингридиента',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='уникальность пары ингридиент-единица измерения',
            ),
        ]

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Tag(models.Model):
    """
    Модель для описания тега.
    """
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True,
        error_messages={
            'unique': 'Указанное имя тега уже существует.',
        },
    )
    color = models.CharField(
        'Цвет в кодировке HEX',
        max_length=7,
        null=True
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=200,
        unique=True,
        error_messages={
            'unique': 'Указанный слаг уже существует.',
        },
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='уникальность пары тег-слаг',
            ),
        ]

    def __str__(self):
        return f'Тег {self.name}, цветовой код - {self.color}'


class Recipe(models.Model):
    """
    Модель для описания рецепта.
    """

    name = models.CharField(
        'Название рецепта',
        max_length=200,
        unique=True,
        error_messages={
            'unique': 'Рецепт с указанным именем уже существует.',
        }
    )
    text = models.TextField(
        'Описание рецепта',
    )
    pub_date = models.DateTimeField(
        'Дата создания рецепта',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        default=1,
        validators=[
            validators.MinValueValidator(
                1,
                message='Минимальное время приготовления 1 минута'
            )
        ]
    )
    image = models.ImageField(
        'Изображение для рецепта',
        upload_to='media_for_recipe/',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта',
        related_name='recipes',
    )
    ingridients = models.ManyToManyField(
        Ingredient,
        through='IngridientRecipe',
        verbose_name='Ингридиент с указанием количества для рецепта',
        related_name='recipes',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(ingridients.through.objects.count()__gte=1),
        #         name=('в рецепте должно быть более 1 ингридиента')
        #     ),
        # ]

    def __str__(self):
        return f'{self.name}, автор {self.author}'

    def _get_number_additions_to_favourite(self):
        """
        Функция вычисляет число добавления рецептов в избранное.
        """
        return self.favourites.count()

    _get_number_additions_to_favourite.short_description = 'в избранном у'

    def _get_number_ingridients(self):
        """
        Функция вычисляет число ингридиентов в рецепте.
        """
        return self.ingridients.through.objects.count()

    _get_number_ingridients.short_description = 'количество ингридиентов'


class IngridientRecipe(models.Model):
    """
    Модель, обеспечивающая связь ингридиента и его количества, необходимого
    для конкретного рецепта.
    """

    ingridient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        'Количество ингридиента в выбранных единицах',
    )

    class Meta:
        verbose_name = 'Ингридиент-количество для рецепта'
        verbose_name_plural = 'Ингридиенты с количествами для рецепта'
        ordering = ('recipe__name',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingridient', 'recipe'],
                name='уникальность ингридиента в рецепте',
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name=('количество ингридиента должно быть больше 0')
            ),
        ]

    def __str__(self):
        return (f'Для рецепта {self.recipe} необходимо {self.quantity} '
                f'{self.ingridient}')


class FavoriteList(models.Model):
    """
    Модель для описания избранных рецептов пользователя.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор списка избранного',
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        related_name='favourites',
    )

    class Meta():
        verbose_name = 'Список избранных рецептов'
        verbose_name_plural = 'Списки избранных рецептов'
        ordering = ('recipes__name',)

    def __str__(self):
        return f'Список избранных рецептов {self.user}'


class ShoppingList(models.Model):
    """
    Модель для описания списка покупок пользователя.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор списка покупок',
        on_delete=models.CASCADE,
        related_name='shoppings',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        related_name='shoppings',
    )

    class Meta():
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('recipes__name',)

    def __str__(self):
        return f'Список покупок пользователя {self.user}'

    # def _get_list_of_ingridients(self):
    #     pass
