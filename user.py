class User:
    def __init__(self, user_id, anime_id, rating):
        self.__user_id = user_id
        self.__anime_id = anime_id
        self.__rating = rating

    def set_user_id(self, user_id):
        self.__user_id = user_id

    def get_user_id(self):
        return self.__user_id

    def set_anime_id(self, anime_id):
        self.__anime_id = anime_id

    def get_anime_id(self):
        return self.__anime_id

    def set_rating(self, rating):
        self.__rating = rating

    def get_rating(self):
        return self.__rating