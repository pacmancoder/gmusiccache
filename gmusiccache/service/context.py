import getpass


class MessageInteraction:
    def __init__(self, message):
        self.message = message

    class Result:
        pass


class StatusInteraction:
    def __init__(self, message):
        self.message = message

    class Result:
        pass


class GetPasswordInteraction:
    def __init__(self, prompt):
        self.prompt = prompt

    class Result:
        def __init__(self, password):
            self.password = password


class QuerySettingsInteraction:
    def __init__(self, key):
        self.key = key

    class Result:
        def __init__(self, value):
            self.value = value


class ExecutionContext:
    def __init__(self, settings):
        self.__settings = settings

    def interact(self, interaction):
        if isinstance(interaction, MessageInteraction):
            print(interaction.message)
            return MessageInteraction.Result()
        elif isinstance(interaction, StatusInteraction):
            print(interaction.message)
            return StatusInteraction.Result()
        elif isinstance(interaction, GetPasswordInteraction):
            return GetPasswordInteraction.Result(getpass.getpass(interaction.prompt + ': '))
        elif isinstance(interaction, QuerySettingsInteraction):
            return QuerySettingsInteraction.Result(getattr(self.__settings, interaction.key, None))