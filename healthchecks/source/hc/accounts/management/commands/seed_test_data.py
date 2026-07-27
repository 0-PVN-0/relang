from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hc.api.models import TokenBucket
from hc.accounts.models import Member, Profile, Project


class Command(BaseCommand):
    help = "Seed database with test data (Alice, Bob, Charlie users + projects)"

    def handle(self, *args, **options):
        TokenBucket.objects.all().delete()

        if User.objects.filter(username="alice").exists():
            self.stdout.write("Test data already exists, skipping")
            return

        alice = User(username="alice", email="alice@example.org")
        alice.set_password("password")
        alice.save()

        project = Project(owner=alice, api_key="X" * 32)
        project.name = "Alices Project"
        project.badge_key = "alice"
        project.ping_key = "p" * 22
        project.save()

        profile = Profile(user=alice)
        profile.sms_limit = 50
        profile.check_limit = 10000
        profile.save()

        bob = User(username="bob", email="bob@example.org")
        bob.set_password("password")
        bob.save()

        bobs_project = Project(owner=bob)
        bobs_project.badge_key = "bob"
        bobs_project.save()

        bobs_profile = Profile(user=bob)
        bobs_profile.save()

        Member.objects.create(user=bob, project=project, role=Member.Role.REGULAR)

        charlie = User(username="charlie", email="charlie@example.org")
        charlie.set_password("password")
        charlie.save()

        charlies_project = Project(owner=charlie)
        charlies_project.badge_key = "charlie"
        charlies_project.save()

        charlies_profile = Profile(user=charlie)
        charlies_profile.save()

        self.stdout.write(f"Test data seeded: alice (project={project.code}), bob, charlie")
