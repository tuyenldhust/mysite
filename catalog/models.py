from django.db import models
from django.urls import reverse
import uuid # Required for unique book instances
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from datetime import date

class Genre(models.Model):
  """Model representing a book genre."""
  name = models.CharField(_('Genre'), max_length=200, help_text=_('Enter a book genre (e.g.Science Fiction)'))

  def __str__(self):
    """String for representing the Model object."""
    return self.name
  
class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(verbose_name=_('Language'), max_length=200,
                            help_text=_("Enter the book's natural language (e.g. English, French, Japanese etc.)"))

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

class Book(models.Model):
  """Model representing a book (but not a specific copy of a book)."""
  title = models.CharField(_('Title'), max_length=200)
  author = models.ForeignKey('Author', verbose_name=_('Author'), on_delete=models.SET_NULL, null=True)
  summary = models.TextField(_('Summary'), max_length=1000, help_text=_('Enter a brief description of the book'))
  isbn = models.CharField('ISBN', max_length=13, unique=True,help_text=_('13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'))
  genre = models.ManyToManyField(Genre, verbose_name=_('Genre'), help_text=_('Select a genre for this book'))
  language = models.ForeignKey('Language',verbose_name=_('Language'), on_delete=models.SET_NULL, null=True)

  class Meta:
    ordering = ['title', 'author']

  def __str__(self):
    """String for representing the Model object."""
    return self.title
  
  def get_absolute_url(self):
    """Returns the url to access a detail record for this book."""
    return reverse('book-detail', args=[str(self.id)])
  
  def display_genre(self):
    """Create a string for the Genre. This is required to display genre in Admin."""
    return ', '.join(genre.name for genre in self.genre.all()[:3])

  display_genre.short_description = 'Genre'
  
class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('Unique ID for this particular bookacross whole library'))
    book = models.ForeignKey('Book', verbose_name=_('Book'), on_delete=models.RESTRICT)
    imprint = models.CharField(_('Imprint'), max_length=200)
    due_back = models.DateField(_('Due back'), null=True, blank=True)
    borrower = models.ForeignKey(User, verbose_name=_('Borrower'), on_delete=models.SET_NULL, null=True, blank=True)
    LOAN_STATUS = (('m', _('Maintenance')),('o', _('On loan')),('a', _('Available')),('r', _('Reserved')),)
    status = models.CharField(_('Status'), max_length=1,choices=LOAN_STATUS,blank=True,default='m',help_text=_('Book availability'),)
    
    class Meta:
       ordering = ['due_back']
       permissions = (("can_mark_returned", _("Set book as returned")),)
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'
    
    @property
    def is_overdue(self):
        return self.due_back and date.today() > self.due_back
    
class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(_('First name'), max_length=100)
    last_name = models.CharField(_('Last name'), max_length=100)
    date_of_birth = models.DateField(_('Birthday'), null=True, blank=True)
    date_of_death = models.DateField(_('Died'), null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
