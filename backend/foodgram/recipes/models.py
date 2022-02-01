from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    """Модель для описания ингридиентов, входящих в рецепты.
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
                fields = ['name', 'measurement_unit'],
                name = 'уникальность пары ингридиент-единица измерения',
            ),
        ]

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Tag(models.Model):
    """Модель для описания тега.
    """
    name=models.CharField(
        'Название тега',
        max_length=200,
        unique=True,
        error_messages={
            'unique': 'Указанное имя тега уже существует.',
        },
    )
    color=models.CharField(
        'Цвет в кодировке HEX',
        max_length=7,
        null=True
    )
    slug=models.SlugField(
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
                fields = ['name', 'slug'],
                name = 'уникальность пары тег-слаг',
            ),
        ]
    
    # def color_name(self):
    #     return webcolors.hex_to_name(self.color)

    def __str__(self):
        return f'Тег {self.name}, цветовой код - {self.color}'


class Recipe(models.Model):
    """Модель для описания рецепта.
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
    )
    # image = models.ImageField(
    #     'Изображение для рецепта',
    #     name = 'recipe_{self.name}'
    # )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта',
        related_name='recipe',
    )
    ingridients = models.ManyToManyField(
        Ingredient,
        through='IngridientRecipe',
        verbose_name='Ингридиент с указанием количества для рецепта',
        related_name='recipe',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.CheckConstraint(
                check = models.Q(cooking_time__gte=1),
                name = ('время приготовления должно быть больше или равно 1 '
                            'минуте')
            ),
        ]
    
    def __str__(self):
        return f'{self.name}, автор {self.author}'


class IngridientRecipe(models.Model):
    """Модель, обеспечивающая связь ингридиента и его количества, необходимого
    для конкретного рецепта.
    """

    ingridient = models.ForeignKey(
        Ingredient,
        verbose_name = 'Ингридиент',
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
        ordering = ('recipe',)
    
    def __str__(self):
        return (f'Для рецепта {self.recipe} необходимо {self.quantity} '
            f'{self.ingridient}')
