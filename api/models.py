from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


class Category(models.Model):
    name = models.CharField("Категория", max_length=30)
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField("Жанр", max_length=30)
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.TextField(max_length=50)
    year = models.PositiveIntegerField(
        verbose_name='Год',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(datetime.date.today().year)
        ]
    )
    description = models.TextField(max_length=200, null=True, blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, related_name="titles", null=True, blank=True
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField('Отзыв')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.IntegerField('Оценка',
                                validators=[MinValueValidator(0),
                                            MaxValueValidator(10)])

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
