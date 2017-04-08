import log
import pickle


# TODO read about exception and add implementation for protect code

class UserDataBase:
    def __init__(self):
        self.file_name = "data"
        self.file_index = 0
        self._get_base()

    def _update(self):
        print(self.table)
        try:
            file_data = open(self.file_name + str(self.file_index), "wb")
        except IsADirectoryError:
            self.file_index += 1
            log.print_to_log("Dump file name changed to " + self.file_name +
                             str(self.file_index) + '\n')
            self._update()
            return
        pickle.dump(self.table, file_data)

    def _get_base(self):
        try:
            file_data = open(self.file_name + str(self.file_index), "rb")
        except FileNotFoundError:
            log.print_to_log("Error in opening file_data\n")
            self.table = {}
            self._update()
            return
        self.table = pickle.load(file_data)

    @staticmethod
    def _make_cell(user_id, user_name, user_credentials):
        return {str(user_id): [user_name, user_credentials]}

    def delete_user(self, user_id):
        self._get_base()
        self.table.pop(str(user_id))
        self._update()

    def create_user(self, user_id, user_name, user_credentials):
        self._get_base()
        self.table.update(self._make_cell(user_id, user_name, user_credentials))
        self._update()

    def change_credentials(self, user_id, user_name, user_credentials):
        self._get_base()
        self.delete_user(user_id)
        self.create_user(user_id, user_name, user_credentials)
        self._update()

    def get_user_credentials(self, user_id):
        self._get_base()
        return self.table.get(str(user_id), 'None')

    @staticmethod
    def check_user_credentials(user_id):
        return True


if __name__ == "__main__":
    a = UserDataBase()
    a.create_user(777, "vasya", "123")
    a.create_user(666, "kolya", "321")
    print(a.table)
    a.delete_user(777)
    print(a.table)
    a.create_user(777, "sereja", "1231")
    print(a.table)
    a.change_credentials(777, "egor", "132")
    print(a.table)
    print(a.get_user_credentials(666))
