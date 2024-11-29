from django.shortcuts import render
from .forms import CityForm
from .weather_api import get_weather_data


def index(request):
    form = CityForm()
    weather_data = None
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            weather_data = get_weather_data(city)

    return render(request,
                  'index.html',
                  {'form': form, 'weather_data': weather_data})
