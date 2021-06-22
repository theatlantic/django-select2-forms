import contextlib
import unittest

import django
from django.conf import settings
from selenosis.testcases import AdminSelenosisTestCase
from selenium.webdriver.common.keys import Keys

from .models import Author, Publisher, Book, Library


def load_fixtures():
    Publisher.objects.bulk_create([
            Publisher(pk=pk, name=name, country=country)
            for pk, name, country in [
                [1, "University of Minnesota Press", "US"],
                [2, "Penguin Press", "US"],
                [3, "Presses Universitaires de France", "FR"],
                [4, "Columbia University Press", "US"],
            ]
        ])

    Author.objects.bulk_create([
            Author(pk=pk, first_name=first, last_name=last, alive=alive)
            for pk, first, last, alive in [
                [1, "Gilles", "Deleuze", False],
                [2, "Félix", "Guattari", False],
                [3, "Thomas", "Pynchon", True],
                [4, "Mark", "Leyner", True],
            ]
        ])


class TestAdmin(AdminSelenosisTestCase):

    root_urlconf = "tests.urls"

    def setUp(self):
        super().setUp()
        load_fixtures()

    def initialize_page(self):
        super(TestAdmin, self).initialize_page()
        self.selenium.execute_script("""(function($) {
            $(document).ready(function() {
                window._select2_test_data = {
                    load_count: 0,
                    open_count: 0,
                    change_count: 0
                };
                $(document).on('select2-open', '.django-select2', function() {
                    window._select2_test_data.open_count++;
                });
                $(document).on('change', '.django-select2', function() {
                    window._select2_test_data.change_count++;
                });
                $(document).on('select2-loaded', '.django-select2', function() {
                    window._select2_test_data.load_count++;
                });
            })
        })(django.jQuery)""")

    def field_is_active(self, field):
        return self.selenium.execute_script(
            'return django.jQuery("#s2id_id_%s").is(".select2-container-active")' % field)

    def save_form(self):
        # Click on header to blur focus from any input elements
        with self.clickable_selector('#content > h1, #grp-content-title > h1') as el:
            el.click()
        super(TestAdmin, self).save_form()

    @contextlib.contextmanager
    def select2_open_dropdown(self, field_name, timeout=None):
        is_m2m = "authors" in field_name

        count_attr = 'open' if is_m2m else 'load'

        def get_count():
            return self.selenium.execute_script(
                "return _select2_test_data.%s_count" % count_attr) or 0

        initial_count = get_count()
        if not self.field_is_active(field_name):
            click_target = '.select2-input' if is_m2m else '.select2-choice'
            with self.clickable_selector("#s2id_id_%s %s" % (field_name, click_target)) as el:
                el.click()
                self.wait_until(
                    lambda d: get_count() > initial_count,
                    timeout=timeout,
                    message="Timeout waiting for %s of field %s" % (count_attr, field_name))
        with self.clickable_selector(".select2-focused") as el:
            yield el

    def get_dropdown_count(self):
        return len(self.selenium.find_elements_by_css_selector(
            '.select2-drop-active .select2-results '
            '.select2-result-selectable:not(.select2-selected)'))

    def select2_send_keys(self, field_name, keys, clear=False, timeout=None):
        count_attr = 'change' if Keys.ENTER in keys else 'load'

        def get_count():
            return self.selenium.execute_script(
                "return _select2_test_data.%s_count" % count_attr) or 0

        with self.select2_open_dropdown(field_name) as el:
            if clear:
                el.clear()
            initial_count = get_count()
            if keys:
                el.send_keys(keys)
                self.wait_until(
                    lambda d: get_count() > initial_count,
                    timeout=timeout,
                    message="Timeout waiting for %s of field %s" % (count_attr, field_name))
            return el

    def test_fk(self):
        book = Book.objects.create(title="Difference and Repetition")
        self.load_admin(book)
        columbia_univ_press = Publisher.objects.get(name='Columbia University Press')
        self.select2_send_keys('publisher', '')
        self.assertEqual(self.get_dropdown_count(), 5)
        self.select2_send_keys('publisher', 'co')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('publisher', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        self.assertEqual(book.publisher, columbia_univ_press)

    def test_fk_limit(self):
        book = Book.objects.create(title="Difference and Repetition")
        self.load_admin(book)
        columbia_univ_press = Publisher.objects.get(name='Columbia University Press')
        self.select2_send_keys('us_publisher', '')
        self.assertEqual(self.get_dropdown_count(), 4)
        self.select2_send_keys('us_publisher', 'co')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('us_publisher', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        self.assertEqual(book.us_publisher, columbia_univ_press)

    def test_fk_ajax(self):
        book = Book.objects.create(title="Difference and Repetition")
        self.load_admin(book)
        columbia_univ_press = Publisher.objects.get(name='Columbia University Press')
        self.select2_send_keys('publisher_ajax', '')
        self.assertEqual(self.get_dropdown_count(), 4)
        self.select2_send_keys('publisher_ajax', 'co')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('publisher_ajax', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        self.assertEqual(book.publisher_ajax, columbia_univ_press)

    def test_fk_limit_ajax(self):
        book = Book.objects.create(title="Difference and Repetition")
        self.load_admin(book)
        columbia_univ_press = Publisher.objects.get(name='Columbia University Press')
        self.select2_send_keys('us_publisher_ajax', '')
        self.assertEqual(self.get_dropdown_count(), 3)
        self.select2_send_keys('us_publisher_ajax', 'co')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('us_publisher_ajax', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        self.assertEqual(book.us_publisher_ajax, columbia_univ_press)

    def test_m2m(self):
        book = Book.objects.create(title="A Thousand Plateaus")
        self.load_admin(book)
        self.select2_send_keys('authors', '')
        self.assertEqual(self.get_dropdown_count(), 4)
        self.select2_send_keys('authors', 'l')
        self.assertEqual(self.get_dropdown_count(), 3)
        self.select2_send_keys('authors', 'euze')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('authors', Keys.ENTER)
        self.select2_send_keys('authors', " %s" % Keys.BACKSPACE)
        self.assertEqual(self.get_dropdown_count(), 3)
        self.select2_send_keys('authors', 'guat')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('authors', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        deleuze = Author.objects.get(last_name='Deleuze')
        guattari = Author.objects.get(last_name='Guattari')
        self.assertEqual(list(book.authors.all()), [deleuze, guattari])

    def test_m2m_ajax(self):
        book = Book.objects.create(title="A Thousand Plateaus")
        self.load_admin(book)
        self.select2_send_keys('authors_ajax', '')
        self.assertEqual(self.get_dropdown_count(), 4)
        self.select2_send_keys('authors_ajax', 'l')
        self.assertEqual(self.get_dropdown_count(), 2)
        self.select2_send_keys('authors_ajax', 'euze')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('authors_ajax', Keys.ENTER)
        self.select2_send_keys('authors_ajax', " %s" % Keys.BACKSPACE)
        self.assertEqual(self.get_dropdown_count(), 3)
        self.select2_send_keys('authors_ajax', 'guat')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('authors_ajax', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        deleuze = Author.objects.get(last_name='Deleuze')
        guattari = Author.objects.get(last_name='Guattari')
        self.assertEqual(list(book.authors_ajax.all()), [deleuze, guattari])

    def test_m2m_limit(self):
        book = Book.objects.create(title="Against the Day")
        self.load_admin(book)
        self.select2_send_keys('alive_authors', '')
        self.assertEqual(self.get_dropdown_count(), 2)
        self.select2_send_keys('alive_authors', 'pync')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('alive_authors', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        pynchon = Author.objects.get(last_name='Pynchon')
        self.assertEqual(list(book.alive_authors.all()), [pynchon])

    def test_m2m_limit_ajax(self):
        book = Book.objects.create(title="Against the Day")
        self.load_admin(book)
        self.select2_send_keys('alive_authors_ajax', '')
        self.assertEqual(self.get_dropdown_count(), 2)
        self.select2_send_keys('alive_authors_ajax', 'pync')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('alive_authors_ajax', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        pynchon = Author.objects.get(last_name='Pynchon')
        self.assertEqual(list(book.alive_authors_ajax.all()), [pynchon])

    def test_m2m_ajax_custom_search_field(self):
        book = Book.objects.create(title="A Thousand Plateaus")
        self.load_admin(book)
        self.select2_send_keys('authors_full_name_ajax', '')
        self.assertEqual(self.get_dropdown_count(), 4)
        self.select2_send_keys('authors_full_name_ajax', 'l')
        self.assertEqual(self.get_dropdown_count(), 3)
        self.select2_send_keys('authors_full_name_ajax', 'euze')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('authors_full_name_ajax', Keys.ENTER)
        self.select2_send_keys('authors_full_name_ajax', " %s" % Keys.BACKSPACE)
        self.assertEqual(self.get_dropdown_count(), 3)
        self.select2_send_keys('authors_full_name_ajax', 'guat')
        self.assertEqual(self.get_dropdown_count(), 1)
        self.select2_send_keys('authors_full_name_ajax', Keys.ENTER)
        self.save_form()
        book.refresh_from_db()
        deleuze = Author.objects.get(last_name='Deleuze')
        guattari = Author.objects.get(last_name='Guattari')
        self.assertEqual(list(book.authors_full_name_ajax.all()), [deleuze, guattari])

    def test_inline_add_init(self):
        if django.VERSION < (1, 9):
            raise unittest.SkipTest("Django 1.8 does not have the formset:added event")
        if 'grappelli' in settings.INSTALLED_APPS:
            raise unittest.SkipTest("django-grappelli does not have the formset:added event")
        library = Library.objects.create(name="Princeton University Library")
        columbia_univ_press = Publisher.objects.get(name='Columbia University Press')
        self.load_admin(library)
        with self.clickable_selector(".add-row a") as el:
            el.click()
        with self.clickable_selector('#id_book_set-0-title') as el:
            el.send_keys('Difference and Repetition')
        self.select2_send_keys('book_set-0-publisher', u'co%s' % Keys.ENTER)
        self.save_form()
        library.refresh_from_db()
        books = library.book_set.all()
        self.assertNotEqual(len(books), 0, "Book inline did not save")
        self.assertEqual(books[0].publisher, columbia_univ_press)
