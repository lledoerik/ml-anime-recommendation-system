class Anime:
    def __init__(self, anime_id, name, members):
        self.__anime_id = anime_id
        self.__name = name
        self.__members = members

    def set_anime_id(self, anime_id):
        self.__anime_id = anime_id

    def get_anime_id(self):
        return self.__anime_id

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_members(self, members):
        self.__members = members

    def get_members(self):
        return self.__members