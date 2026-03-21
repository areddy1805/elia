import os


class DocumentLoader:

    def __init__(self, base_path="data/documents"):
        self.base_path = base_path

    def normalize_application_id(self, application_id: str):
        """
        Convert:
        APP001 → app_001
        """
        num = application_id.replace("APP", "")
        return f"app_{num}"

    def load_documents(self, application_id):

        folder_name = self.normalize_application_id(application_id)
        app_path = os.path.join(self.base_path, folder_name)

        docs = {}

        # -------------------
        # SAFE HANDLING (CRITICAL)
        # -------------------
        if not os.path.exists(app_path):
            return docs  # return empty instead of crashing

        for file in os.listdir(app_path):
            file_path = os.path.join(app_path, file)

            if not os.path.isfile(file_path):
                continue

            try:
                with open(file_path) as f:
                    docs[file] = f.read()
            except:
                docs[file] = ""

        return docs