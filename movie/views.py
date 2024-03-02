from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from .models import Movie

# Create your views here.

def home(request):
    # return HttpResponse('<h1>Movie Review Home</h1>')
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})

def statistics_view(request):
    # Obtener todos los años de las películas
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {}
    for year in years:
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = "None"
        count = movies_in_year.count()
        movie_counts_by_year[year] = count

    # Generar gráfica de cantidad de películas por año
    plt.figure(figsize=(10, 5)) # Ajustar tamaño de la figura para acomodar dos gráficas
    plt.subplot(1, 2, 1) # Primera subgráfica para películas por año
    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    # Obtener todos los géneros únicos considerando solo el primer género listado
    genres = Movie.objects.values_list('genre', flat=True)
    unique_genres = set(genre.split(',')[0] for genre in genres if genre) # Asumiendo que los géneros están separados por comas
    movie_counts_by_genre = {}
    for genre in unique_genres:
        movies_in_genre = Movie.objects.filter(genre__startswith=genre)
        count = movies_in_genre.count()
        movie_counts_by_genre[genre] = count

    # Generar gráfica de cantidad de películas por género
    plt.subplot(1, 2, 2) # Segunda subgráfica para películas por género
    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_genre))
    plt.bar(bar_positions, movie_counts_by_genre.values(), width=bar_width, align='center')
    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_genre.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    # Guardar ambas gráficas en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight') # Asegurarse de que todo el contenido se incluya en la imagen
    buffer.seek(0)
    plt.close()

    # Convertir la gráfica a base64 para su uso en el template
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Renderizar la plantilla statistics.html con las gráficas
    return render(request, 'statistics.html', {'graphic': graphic})