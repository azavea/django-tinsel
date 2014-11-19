# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import django
from django.contrib.auth.models import User
from django.http import (HttpResponseNotAllowed, Http404, HttpResponseRedirect,
                         HttpResponseBadRequest)
from django.test import TestCase, RequestFactory
from django.utils.six import StringIO
from django.views.decorators.http import require_POST, require_GET

from .context import django_tinsel  # NOQA
from django_tinsel.decorators import (route, log, render_template,
                                      json_api_call, string_to_response,
                                      username_matches_request_user)
from django_tinsel.utils import decorate


# Test helpers:
def string_view(request):
    return "Hello World"


def dict_view(request):
    return {"Hello": "World"}


def redirect_view(request):
    return HttpResponseRedirect("http://lmgtfy.com")


def bad_response_view(request):
    return HttpResponseBadRequest("Goodbye World")


@username_matches_request_user
def user_view(request, user):
    return user.username


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_req = self.factory.get('fake/url')
        self.post_req = self.factory.post('fake/url')
        self.put_req = self.factory.put('fake/url')


# Actual tests
class DecorateTests(BaseTestCase):
    def test_decorate(self):
        self.assertEqual("Hello World", string_view(self.get_req))

        post_view = decorate(require_POST, string_view)
        get_view = decorate(require_GET, string_view)

        self.assertIsInstance(get_view(self.post_req), HttpResponseNotAllowed)
        self.assertIsInstance(post_view(self.get_req), HttpResponseNotAllowed)

        self.assertEqual("Hello World", get_view(self.get_req))
        self.assertEqual("Hello World", post_view(self.post_req))


class RouteTests(BaseTestCase):
    def test_routing(self):
        routed_view = route(GET=string_view, POST=dict_view)

        self.assertEqual("Hello World", routed_view(self.get_req))
        self.assertEqual({"Hello": "World"}, routed_view(self.post_req))

        with self.assertRaises(Http404):
            routed_view(self.put_req)

    def test_else(self):
        routed_view = route(GET=string_view, ELSE=dict_view)

        self.assertEqual("Hello World", routed_view(self.get_req))
        self.assertEqual({"Hello": "World"}, routed_view(self.post_req))
        self.assertEqual({"Hello": "World"}, routed_view(self.put_req))


class LogTest(BaseTestCase):
    def test_logging(self):
        output = StringIO()

        logging_view = decorate(log("Got a request", out=output), string_view)

        self.assertEqual("Hello World", logging_view(self.get_req))
        output.seek(0)
        self.assertEqual("Got a request\n", output.read())


class RenderTemplateTests(BaseTestCase):
    def test_callable(self):
        templating_view = decorate(render_template("home.html"), dict_view)
        resp = templating_view(self.get_req)

        self.assertEqual(b"I said hello to World\n", resp.content)

    def test_dict(self):
        templating_view = decorate(render_template("home.html"),
                                   {"Hello": "Joe"})
        resp = templating_view(self.get_req)

        self.assertEqual(b"I said hello to Joe\n", resp.content)

    def test_view_returns_reponse(self):
        templating_view = decorate(render_template("home.html"),
                                   redirect_view)
        resp = templating_view(self.get_req)

        self.assertEqual(b"", resp.content)
        if django.VERSION[1] > 5:
            self.assertEqual("http://lmgtfy.com", resp.url)

    def test_status_code(self):
        templating_view = render_template("home.html")(dict_view, 500)
        resp = templating_view(self.get_req)

        self.assertEqual(b"I said hello to World\n", resp.content)
        self.assertEqual(500, resp.status_code)


class JsonApiCallTests(BaseTestCase):
    def test_simple_dict_to_json(self):
        json_view = json_api_call(dict_view)
        resp = json_view(self.get_req)

        self.assertEqual(b'{"Hello": "World"}', resp.content)
        self.assertEqual("application/json", resp['Content-Type'])
        self.assertEqual('18', resp['Content-Length'])

    def test_view_returns_response(self):
        json_view = json_api_call(redirect_view)
        resp = json_view(self.get_req)

        self.assertEqual(b"", resp.content)
        if django.VERSION[1] > 5:
            self.assertEqual("http://lmgtfy.com", resp.url)


class StringToResponseTests(BaseTestCase):
    def test_csv_view(self):
        csv_view = string_to_response("text/csv")(lambda req: "key,val\na,1")
        resp = csv_view(self.get_req)

        self.assertEqual(b'key,val\na,1', resp.content)
        self.assertEqual("text/csv", resp['Content-Type'])
        self.assertEqual('11', resp['Content-Length'])


class UsernameMatchesRequestUserTests(BaseTestCase):
    def setUp(self):
        super(UsernameMatchesRequestUserTests, self).setUp()
        self.bender = User.objects.create(username='bender')
        self.leela = User.objects.create(username='leela')

    def test_forbidden(self):
        req = self.factory.get('fake/url')
        req.user = self.bender
        resp = user_view(req, username='leela')

        self.assertEqual(403, resp.status_code)

    def test_404(self):
        req = self.factory.get('fake/url')
        req.user = self.bender

        with self.assertRaises(Http404):
            user_view(req, username='yancy')

    def test_working(self):
        req = self.factory.get('fake/url')
        req.user = self.bender
        resp = user_view(req, username='bender')

        self.assertEqual('bender', resp)
