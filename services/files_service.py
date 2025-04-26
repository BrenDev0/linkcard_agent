import pandas
import io

class FilesService:
    def parse_file(filename: str, content: bytes) -> list[list[str]]:
        if filename.endswith(".csv"):
            df = pandas.read_csv(io.BytesIO(content), header=None)
        elif filename.endswith((".xlsx", ".xls")):
            df = pandas.read_excel(io.BytesIO(content), engine="openpyxl", header=None)
        else:
            raise ValueError("Unsupported file type")

        return df.astype(str).values.tolist()
