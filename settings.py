from os import environ

SESSION_CONFIGS = [
    dict(
        name="observe",
        app_sequence=["observe"],
        num_demo_participants = 2
    ),
    dict(
        name="simple_pd",
        app_sequence=["simple_pd"],
        num_demo_participants=2
    ),
    dict(
        name="simple_tg",
        app_sequence={"simple_tg"},
        num_demo_participants = 2,
        players_per_group =2,
        ),
    dict(
        name="simple_sd",
        app_sequence=["simple_sd"],
        num_demo_participants=3,
        players_per_group=3,
    ),
    dict(
        name="user_friendly_sd",
        app_sequence=["user_friendly_sd"],
        num_demo_participants=3,
        players_per_group=3,
    ),
]


if "DATABASE_URL" in environ:
    del environ["DATABASE_URL"]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "9372863799180"
