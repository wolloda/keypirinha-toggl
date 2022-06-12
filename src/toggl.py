# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet

from .toggler import Toggler

class Toggl(kp.Plugin):
    """
    One-line description of your plugin.

    This block is a longer and more detailed description of your plugin that may
    span on several lines, albeit not being required by the application.

    You may have several plugins defined in this module. It can be useful to
    logically separate the features of your package. All your plugin classes
    will be instantiated by Keypirinha as long as they are derived directly or
    indirectly from :py:class:`keypirinha.Plugin` (aliased ``kp.Plugin`` here).

    In case you want to have a base class for your plugins, you must prefix its
    name with an underscore (``_``) to indicate Keypirinha it is not meant to be
    instantiated directly.

    In rare cases, you may need an even more powerful way of telling Keypirinha
    what classes to instantiate: the ``__keypirinha_plugins__`` global variable
    may be declared in this module. It can be either an iterable of class
    objects derived from :py:class:`keypirinha.Plugin`; or, even more dynamic,
    it can be a callable that returns an iterable of class objects. Check out
    the ``StressTest`` example from the SDK for an example.

    Up to 100 plugins are supported per module.

    More detailed documentation at: http://keypirinha.com/api/plugin.html
    """

    TOGGL_CATEGORY = kp.ItemCategory.USER_BASE + 1
    TOGGL_TIMER_ENTRY = kp.ItemCategory.USER_BASE + 2
    DEFAULT_ICON = "res://Toggl/img/toggl_logo.png"

    def __init__(self):
        super().__init__()

    def on_start(self):
        self._read_config()
        self._toggl = Toggler(self._TOGGL_API_TOKEN)
        self._projects = self._toggl.get_projects(self._TOGGL_WORKSPACE_ID)

        self.set_default_icon(self.load_icon(self.DEFAULT_ICON))

    def on_catalog(self):
        catalog = [
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label="Toggl: Start timer",
                short_desc="Select a project and start timer",
                target="select_project",
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            ),
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label="Toggl: Stop timer",
                short_desc="Stop running Toggl timer",
                target="stop_timer",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS)
        ]

        self.set_catalog(catalog)

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        suggestions = []

        if items_chain[-1].target() == "select_project":
            for suggestion in self._projects:

                label = suggestion["name"]

                if suggestion["client"]:
                    label = f"{suggestion['client']}: {suggestion['name']}"


                suggestions.append(
                    self.create_item(
                        category = self.TOGGL_CATEGORY,
                        label = label,
                        short_desc = suggestion["name"],
                        target = suggestion["id"],
                        args_hint = kp.ItemArgsHint.REQUIRED,
                        hit_hint = kp.ItemHitHint.IGNORE,
                        data_bag = "start_timer"
                    )
                )

        elif items_chain[-1].data_bag() == "start_timer":
            if not user_input:
                return

            suggestions = [
                self.create_item(
                    category = self.TOGGL_TIMER_ENTRY,
                    label = user_input,
                    short_desc = user_input,
                    target = "start_timer",
                    args_hint = kp.ItemArgsHint.FORBIDDEN,
                    hit_hint = kp.ItemHitHint.IGNORE,
                    data_bag = items_chain[-1].target()
                )]

        self.set_suggestions(suggestions)


    def on_execute(self, item, action):
        if item.category() == kp.ItemCategory.KEYWORD and item.target() == "stop_timer":
            self._toggl.stop_timer()
            self.info("Runing timer stopped")

        if item.category() == self.TOGGL_TIMER_ENTRY and item.target() == "start_timer":
            self.info(item.label())
            self.info(item.data_bag())
            self._toggl.start_timer(
                item.label(),
                item.data_bag()
            )

            self.info(f"Timer {item.label()} started")

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        self._reload_config()
        self.on_catalog()

    def _read_config(self):
        settings = self.load_settings()
        self._TOGGL_API_TOKEN = settings.get("api_token", "var", unquote=True)
        self._TOGGL_WORKSPACE_ID = settings.get("workspace_id", "var", unquote=True)

