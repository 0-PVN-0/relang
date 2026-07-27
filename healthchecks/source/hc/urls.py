from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import include, path

from hc.accounts import views as accounts_views


def _test_reset(request: HttpRequest) -> HttpResponse:
    from hc.api.models import TokenBucket, Check, Channel
    from hc.accounts.models import Project, Member, Profile
    from django.contrib.auth import get_user_model

    TokenBucket.objects.all().delete()
    Check.objects.all().delete()
    Channel.objects.all().delete()

    User = get_user_model()
    User.objects.exclude(username__in=("alice", "bob", "charlie")).delete()

    Project.objects.exclude(owner__username__in=("alice", "bob", "charlie")).delete()

    for username in ("alice", "bob", "charlie"):
        user = User.objects.get(username=username)
        Project.objects.filter(owner=user).delete()

    alice_project = None
    for username in ("alice", "bob", "charlie"):
        user = User.objects.get(username=username)
        project = Project(owner=user)
        if username == "alice":
            project.name = "Alices Project"
            project.badge_key = "alice"
            project.api_key = "X" * 32
            project.api_key_readonly = "R" * 32
            project.ping_key = "p" * 22
        elif username == "bob":
            project.badge_key = "bob"
        elif username == "charlie":
            project.badge_key = "charlie"
        project.save()
        if username == "alice":
            alice_project = project

    bob = User.objects.get(username="bob")
    if not Member.objects.filter(user=bob, project=alice_project).exists():
        Member.objects.create(user=bob, project=alice_project, role=Member.Role.REGULAR)

    for username in ("alice", "bob", "charlie"):
        user = User.objects.get(username=username)
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.theme = None
        profile.save()

    return HttpResponse("ok")

prefix = ""
if _path := urlparse(settings.SITE_ROOT).path.lstrip("/"):
    prefix = f"{_path}/"

urlpatterns = [
    path(f"{prefix}__test/reset/", _test_reset),
    path(f"{prefix}admin/login/", accounts_views.login),
    path(f"{prefix}admin/", admin.site.urls),
    path(prefix, include("hc.accounts.urls")),
    path(prefix, include("hc.api.urls")),
    path(prefix, include("hc.front.urls")),
    path(prefix, include("hc.payments.urls")),
    path(prefix, include("hc.integrations.apprise.urls")),
    path(prefix, include("hc.integrations.call.urls")),
    path(prefix, include("hc.integrations.discord.urls")),
    path(prefix, include("hc.integrations.email.urls")),
    path(prefix, include("hc.integrations.github.urls")),
    path(prefix, include("hc.integrations.googlechat.urls")),
    path(prefix, include("hc.integrations.gotify.urls")),
    path(prefix, include("hc.integrations.group.urls")),
    path(prefix, include("hc.integrations.matrix.urls")),
    path(prefix, include("hc.integrations.mattermost.urls")),
    path(prefix, include("hc.integrations.msteamsw.urls")),
    path(prefix, include("hc.integrations.ntfy.urls")),
    path(prefix, include("hc.integrations.opsgenie.urls")),
    path(prefix, include("hc.integrations.pagertree.urls")),
    path(prefix, include("hc.integrations.pd.urls")),
    path(prefix, include("hc.integrations.po.urls")),
    path(prefix, include("hc.integrations.prometheus.urls")),
    path(prefix, include("hc.integrations.pushbullet.urls")),
    path(prefix, include("hc.integrations.rocketchat.urls")),
    path(prefix, include("hc.integrations.shell.urls")),
    path(prefix, include("hc.integrations.signal.urls")),
    path(prefix, include("hc.integrations.slack.urls")),
    path(prefix, include("hc.integrations.sms.urls")),
    path(prefix, include("hc.integrations.spike.urls")),
    path(prefix, include("hc.integrations.telegram.urls")),
    path(prefix, include("hc.integrations.trello.urls")),
    path(prefix, include("hc.integrations.victorops.urls")),
    path(prefix, include("hc.integrations.webhook.urls")),
    path(prefix, include("hc.integrations.whatsapp.urls")),
    path(prefix, include("hc.integrations.zulip.urls")),
]
