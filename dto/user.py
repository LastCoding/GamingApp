class User():

    id = 0
    created_date = 0
    email = "e"
    username = "a"

    def __init__(self, UserModel) -> None:
        self.id = UserModel.id
        self.created_date = UserModel.created_date
        self.email = UserModel.email
        self.username = UserModel.username