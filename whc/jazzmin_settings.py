from django.conf import settings
from django.utils.translation import gettext_lazy as _

JAZZMIN_SETTINGS = {
    "site_title": "White Bridge Club - Admin",

    "site_header": "White Bridge Club",

    "site_brand": "White Bridge Club - Admin",

    # "site_logo": "images/logo.png",

    "site_logo_classes": "img-circle",

    "site_icon": "images/favicon.png",

    "welcome_sign": _("Welcome to White Bridge Club"),

    "copyright": "White Bridge Club LLC",
    "search_model": "api.User",

    "user_avatar": "profile.photo",

    ############
    # Top Menu #
    ############

    "topmenu_links": [
        {"name": _("Home"),  "url": "admin:index", "permissions": ["auth.view_user"]},

        {"name": _("Site"), "url": settings.SITE_FRONT_END_URL, "new_window": True},

        {"model": "api.User"},

        {"app": "api"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"model": "api.User"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,
   # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [""],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [
        "auth",
        "api.User",
        "api.Profile",
        "api.Referal",
        "api.SubscribeEmail",
        "api.SearchTerm",
        "api.Category",
        "api.Entity",
	"api.Banner",
        "api.Like",
	"api.Notification",
 	"api.TemplateMessage",
        "api.View",
        "api.Gender",
        "api.CryptoContent",
        "api.ContactLink",
        "api.ShareLink",
        "api.StaticTranslation",
        "api",
    ],

    # Custom links to append to app groups, keyed on app name
    # "custom_links": {
    #     "books": [{
    #         "name": "Make Messages",
    #         "url": "make_messages",
    #         "icon": "fas fa-comments",
    #         "permissions": ["books.view_book"]
    #     }]
    # },

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.1$
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-user-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "api.Category": "fas fa-folder",
        "api.ContactLink": "fas fa-users",
        "api.CryptoContent": "fab fa-bitcoin",
        "api.Entity": "fab fa-adversal",
        "api.Gender": "fas fa-venus-mars",
       	"api.Banner": "fas fa-bullhorn",
        "api.Like": "fas fa-thumbs-up",
	"api.Notification": "fas fa-folder",
	"api.TemplateMessage": "fas fa-folder",
        "api.Profile": "fas fa-user-circle",
        "api.Referal": "fas fa-user-friends",
        "api.SearchTerm": "fab fa-searchengin",
        "api.ShareLink": "fab fa-staylinked",
        "api.StaticTranslation": "fas fa-language",
        "api.SubscribeEmail": "fas fa-envelope",
        "api.User": "fas fa-user",
        "api.View": "fas fa-eye",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
  #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": True,
}
