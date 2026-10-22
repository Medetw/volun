import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from apps.users.models import UserRole, OrganizationType
from apps.projects.models import Category, Region, Project, ProjectFormat, ProjectStatus
from apps.applications.models import Application, ApplicationStatus
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    role = fuzzy.FuzzyChoice([UserRole.VOLUNTEER, UserRole.ORGANIZATION, UserRole.ADMIN])
    phone = factory.Faker("phone_number")
    is_active = True


class VolunteerUserFactory(UserFactory):
    """Factory for Volunteer users."""
    
    role = UserRole.VOLUNTEER


class OrganizationUserFactory(UserFactory):
    """Factory for Organization users."""
    
    role = UserRole.ORGANIZATION


class AdminUserFactory(UserFactory):
    """Factory for Admin users."""
    
    role = UserRole.ADMIN


class VolunteerProfileFactory(factory.django.DjangoModelFactory):
    """Factory for VolunteerProfile model."""
    
    class Meta:
        model = "users.VolunteerProfile"
    
    user = factory.SubFactory(VolunteerUserFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    birth_date = factory.Faker("date_of_birth", minimum_age=18, maximum_age=65)
    gender = fuzzy.FuzzyChoice(["male", "female", "other"])
    city = factory.Faker("city")
    region = factory.Faker("state")
    skills = factory.LazyFunction(lambda: fuzzy.FuzzyChoice([
        ["teaching", "mentoring"],
        ["programming", "web development"],
        ["design", "marketing"],
        ["healthcare", "first aid"],
        ["environmental", "sustainability"]
    ).fuzz())
    interests = factory.LazyFunction(lambda: fuzzy.FuzzyChoice([
        ["education", "children"],
        ["technology", "innovation"],
        ["environment", "conservation"],
        ["health", "wellness"],
        ["arts", "culture"]
    ]).fuzz())
    volunteer_hours = fuzzy.FuzzyInteger(0, 1000)


class OrganizationProfileFactory(factory.django.DjangoModelFactory):
    """Factory for OrganizationProfile model."""
    
    class Meta:
        model = "users.OrganizationProfile"
    
    user = factory.SubFactory(OrganizationUserFactory)
    name = factory.Faker("company")
    organization_type = fuzzy.FuzzyChoice([OrganizationType.NGO, OrganizationType.INITIATIVE_GROUP, OrganizationType.GOVERNMENT])
    description = factory.Faker("text", max_nb_chars=500)
    region = factory.Faker("state")
    contacts = factory.LazyFunction(lambda: {
        "phone": factory.Faker("phone_number").generate(),
        "email": factory.Faker("company_email").generate(),
        "website": factory.Faker("url").generate()
    })
    is_verified = fuzzy.FuzzyChoice([True, False])


class CategoryFactory(factory.django.DjangoModelFactory):
    """Factory for Category model."""
    
    class Meta:
        model = "projects.Category"
    
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=200)


class RegionFactory(factory.django.DjangoModelFactory):
    """Factory for Region model."""
    
    class Meta:
        model = "projects.Region"
    
    name = factory.Faker("state")
    code = factory.Faker("state_abbr")


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for Project model."""
    
    class Meta:
        model = "projects.Project"
    
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text", max_nb_chars=1000)
    category = factory.SubFactory(CategoryFactory)
    organization = factory.SubFactory(OrganizationUserFactory)
    format = fuzzy.FuzzyChoice([ProjectFormat.ONLINE, ProjectFormat.OFFLINE, ProjectFormat.HYBRID])
    region = factory.SubFactory(RegionFactory)
    start_date = factory.Faker("date_between", start_date="-1y", end_date="+1y")
    end_date = factory.Faker("date_between", start_date="today", end_date="+2y")
    volunteers_needed = fuzzy.FuzzyInteger(1, 100)
    status = fuzzy.FuzzyChoice([ProjectStatus.DRAFT, ProjectStatus.ACTIVE, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED])
    requirements = factory.Faker("text", max_nb_chars=300)
    contact_info = factory.LazyFunction(lambda: {
        "phone": factory.Faker("phone_number").generate(),
        "email": factory.Faker("company_email").generate(),
        "address": factory.Faker("address").generate()
    })
    
    @factory.post_generation
    def ensure_end_after_start(obj, create, extracted, **kwargs):
        """Ensure end_date is after start_date."""
        if obj.start_date and obj.end_date and obj.end_date < obj.start_date:
            obj.end_date = obj.start_date + factory.Faker("timedelta", days=30).generate()
            if create:
                obj.save()


class ActiveProjectFactory(ProjectFactory):
    """Factory for active projects."""
    
    status = ProjectStatus.ACTIVE


class DraftProjectFactory(ProjectFactory):
    """Factory for draft projects."""
    
    status = ProjectStatus.DRAFT


class ApplicationFactory(factory.django.DjangoModelFactory):
    """Factory for Application model."""
    
    class Meta:
        model = "applications.Application"
    
    volunteer = factory.SubFactory(VolunteerUserFactory)
    project = factory.SubFactory(ActiveProjectFactory)
    status = fuzzy.FuzzyChoice([ApplicationStatus.PENDING, ApplicationStatus.APPROVED, ApplicationStatus.REJECTED, ApplicationStatus.CANCELLED])
    cover_letter = factory.Faker("text", max_nb_chars=500)
    hours_committed = fuzzy.FuzzyInteger(1, 40)
    review_comment = factory.Faker("text", max_nb_chars=300)


class PendingApplicationFactory(ApplicationFactory):
    """Factory for pending applications."""
    
    status = ApplicationStatus.PENDING


class ApprovedApplicationFactory(ApplicationFactory):
    """Factory for approved applications."""
    
    status = ApplicationStatus.APPROVED


class ProjectReportFactory(factory.django.DjangoModelFactory):
    """Factory for ProjectReport model."""
    
    class Meta:
        model = "reports.ProjectReport"
    
    project = factory.SubFactory(ActiveProjectFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text", max_nb_chars=1000)
    goals_achieved = factory.Faker("text", max_nb_chars=500)
    challenges_faced = factory.Faker("text", max_nb_chars=300)
    total_volunteers_participated = fuzzy.FuzzyInteger(1, 100)
    total_volunteer_hours = fuzzy.FuzzyInteger(1, 1000)
    beneficiaries_count = fuzzy.FuzzyInteger(1, 1000)
    photos = factory.LazyFunction(lambda: [
        factory.Faker("image_url").generate(),
        factory.Faker("image_url").generate()
    ])
    lessons_learned = factory.Faker("text", max_nb_chars=300)
    future_plans = factory.Faker("text", max_nb_chars=300)
    status = fuzzy.FuzzyChoice([ReportStatus.DRAFT, ReportStatus.SUBMITTED, ReportStatus.APPROVED, ReportStatus.REJECTED])
    review_comment = factory.Faker("text", max_nb_chars=300)


class DraftReportFactory(ProjectReportFactory):
    """Factory for draft reports."""
    
    status = ReportStatus.DRAFT


class SubmittedReportFactory(ProjectReportFactory):
    """Factory for submitted reports."""
    
    status = ReportStatus.SUBMITTED


class ApprovedReportFactory(ProjectReportFactory):
    """Factory for approved reports."""
    
    status = ReportStatus.APPROVED


class VolunteerContributionFactory(factory.django.DjangoModelFactory):
    """Factory for VolunteerContribution model."""
    
    class Meta:
        model = "reports.VolunteerContribution"
    
    report = factory.SubFactory(ProjectReportFactory)
    volunteer = factory.SubFactory(VolunteerUserFactory)
    hours_contributed = fuzzy.FuzzyInteger(1, 100)
    tasks_completed = factory.Faker("text", max_nb_chars=500)
    impact_description = factory.Faker("text", max_nb_chars=300)
    performance_rating = fuzzy.FuzzyInteger(1, 5)
    feedback = factory.Faker("text", max_nb_chars=300)


# Batch creation helpers
def create_test_data():
    """Create a comprehensive set of test data."""
    
    # Create users
    admin = AdminUserFactory()
    org1 = OrganizationUserFactory(username="org1")
    org2 = OrganizationUserFactory(username="org2")
    volunteer1 = VolunteerUserFactory(username="volunteer1")
    volunteer2 = VolunteerUserFactory(username="volunteer2")
    volunteer3 = VolunteerUserFactory(username="volunteer3")
    
    # Create profiles
    VolunteerProfileFactory(user=volunteer1)
    VolunteerProfileFactory(user=volunteer2)
    VolunteerProfileFactory(user=volunteer3)
    OrganizationProfileFactory(user=org1)
    OrganizationProfileFactory(user=org2)
    
    # Create categories and regions
    categories = [CategoryFactory() for _ in range(5)]
    regions = [RegionFactory() for _ in range(3)]
    
    # Create projects
    projects = []
    for org in [org1, org2]:
        for i in range(3):
            project = ActiveProjectFactory(
                organization=org,
                category=fuzzy.FuzzyChoice(categories).fuzz(),
                region=fuzzy.FuzzyChoice(regions).fuzz()
            )
            projects.append(project)
    
    # Create applications
    applications = []
    for volunteer in [volunteer1, volunteer2, volunteer3]:
        for project in projects[:2]:  # Apply to first 2 projects
            try:
                app = PendingApplicationFactory(volunteer=volunteer, project=project)
                applications.append(app)
            except Exception:
                pass  # Skip if unique constraint violated
    
    # Approve some applications
    for app in applications[:3]:
        app.status = ApplicationStatus.APPROVED
        app.save()
    
    # Create reports for projects
    reports = []
    for project in projects[:2]:
        report = ProjectReportFactory(project=project)
        reports.append(report)
        
        # Create contributions for approved applications
        approved_apps = project.applications.filter(status=ApplicationStatus.APPROVED)
        for app in approved_apps:
            VolunteerContributionFactory(
                report=report,
                volunteer=app.volunteer,
                hours_contributed=app.hours_committed
            )
    
    return {
        'users': [admin, org1, org2, volunteer1, volunteer2, volunteer3],
        'categories': categories,
        'regions': regions,
        'projects': projects,
        'applications': applications,
        'reports': reports
    }
