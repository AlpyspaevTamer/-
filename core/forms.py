from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import inlineformset_factory
from .models import *
from .models import User, Lecture, Category, Tag, Test, Question, Answer, VideoLecture, Exercise, DictionaryEntry, StudyGroup

#--------------------- Lecture Form -------------------------
class LectureForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Описание (необязательно)'
        }),
        label="Описание"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['image'].required = False
        if self.instance and self.instance.pk:
            self.fields['file'].required = False

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if self.instance and self.instance.pk:
            if not uploaded_file:
                return self.instance.file
        if not self.instance.pk and not uploaded_file:
            raise ValidationError("Необходимо загрузить файл лекции")
        return uploaded_file

    class Meta:
        model = Lecture
        fields = ['title', 'description', 'content', 'image', 'file', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название лекции'}),
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'placeholder': 'Дополнительный контент лекции'}),
            'file': forms.FileInput(attrs={'accept': '.doc,.docx', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control', 'data-placeholder': 'Выберите категорию'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'data-placeholder': 'Выберите теги'}),
        }
        labels = {
            'title': 'Название лекции', 'file': 'Файл лекции (DOC/DOCX)', 'image': 'Обложка лекции',
            'content': 'Дополнительный контент', 'category': 'Категория', 'tags': 'Теги'
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.author = self.initial.get('author')
        if commit:
            instance.save()
            self.save_m2m()
        return instance

#--------------------- Test Form -------------------------
class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'time_limit', 'password', 'group', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название теста'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль (Необязательно)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание теста'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Время на прохождение (минуты)'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {'time_limit': 'Лимит времени (мин)', 'group': 'Доступная группа (опционально)'}

class TestPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}), label="Пароль")

#--------------------- Question & Answer Forms -------------------------
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Текст вопроса'}),
        }

    def __init__(self, *args, **kwargs):
        self.test = kwargs.pop('test', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.test: instance.test = self.test
        if commit: instance.save()
        return instance

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Текст ответа'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'h-5 w-5'}),
        }

class BaseAnswerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return
        
        # Считаем только заполненные ответы
        filled_answers = [f for f in self.forms if f.cleaned_data.get('text')]
        correct_answers = sum(1 for f in filled_answers if f.cleaned_data.get('is_correct', False))
        
        q_type = self.instance.question_type if self.instance else 'single'
        
        if filled_answers:
            if q_type == 'single' and correct_answers != 1:
                raise forms.ValidationError("Для одиночного выбора должен быть 1 правильный ответ")
            if q_type == 'multiple' and correct_answers < 1:
                raise forms.ValidationError("Для множественного выбора должен быть хотя бы 1 правильный ответ")

# Фабрика для 10 полей
AnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    form=AnswerForm, 
    formset=BaseAnswerFormSet,
    extra=10, 
    max_num=10,
    can_delete=False 
)


#--------------------- Auth & Other Forms -------------------------
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}), label="Электронная почта")
    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}), label="Имя пользователя")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}), label="Пароль")

class VideoLectureForm(forms.ModelForm):
    class Meta:
        model = VideoLecture
        fields = ['title', 'description', 'youtube_url', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название видеолекции'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Подробное описание'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube ссылка'}),
        }
    def clean_youtube_url(self):
        url = self.cleaned_data.get('youtube_url')
        if not ('youtube.com/watch?v=' in url or 'youtu.be/' in url):
            raise ValidationError("Введите корректную ссылку на YouTube")
        return url

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'description', 'file']
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and file.name.split('.')[-1].lower() != 'pdf':
            raise ValidationError("Разрешены только PDF-файлы")
        return file

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['title', 'image', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'placeholder': 'Название'}),
            'image': forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-700', 'accept': 'image/*'}),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-700', 'accept': '.pdf'}),
        }

class DictionaryEntryForm(forms.ModelForm):
    class Meta:
        model = DictionaryEntry
        fields = ['word', 'definition']
        widgets = {
            'word': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Слово'}),
            'definition': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Определение', 'rows': 4}),
        }

class AssignGroupForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=StudyGroup.objects.all(), label="Выберите группу", empty_label="Без группы")
    class Meta:
        model = User
        fields = ['group']