from django.test import TestCase
from weather.weather_api import weather_interpretation_codes, wind_directions, pressure_converter


class WeatherInterpretationCodesTestCase(TestCase):

    def test_weather_interpretation_codes(self):
        # Проверяем корректность интерпретации кодов погоды
        self.assertEqual(weather_interpretation_codes("0"), "Ясно")
        self.assertEqual(weather_interpretation_codes("45"), "Туман")
        self.assertEqual(weather_interpretation_codes("95"), "Гроза")

        # Проверяем работу с некорректными кодами
        self.assertEqual(weather_interpretation_codes(999), 'Погодные условия не определены')
        self.assertEqual(weather_interpretation_codes(None), 'Погодные условия не определены')
        self.assertEqual(weather_interpretation_codes("4"), 'Погодные условия не определены')


class WindDirectionsTestCase(TestCase):

    def test_wind_directions(self):
        # Проверяем корректность преобразования углов в направления
        self.assertEqual(wind_directions(0), 'с')
        self.assertEqual(wind_directions(360), 'с')
        self.assertEqual(wind_directions(45), 'св')
        self.assertEqual(wind_directions(90), 'в')
        self.assertEqual(wind_directions(135), 'юв')
        self.assertEqual(wind_directions(180), 'ю')
        self.assertEqual(wind_directions(225), 'юз')
        self.assertEqual(wind_directions(270), 'з')
        self.assertEqual(wind_directions(315), 'сз')


class PressureConverterTestCase(TestCase):

    def test_pressure_converter(self):
        # Проверяем корректность преобразования давления
        self.assertAlmostEqual(pressure_converter(1013), 759.814, places=1)
        self.assertAlmostEqual(pressure_converter(1000), 750.064, places=1)
        self.assertAlmostEqual(pressure_converter(950), 712.558, places=1)
        self.assertAlmostEqual(pressure_converter("950"), -1, places=1)
