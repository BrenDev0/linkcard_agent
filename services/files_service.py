import pandas as pd
import io
from typing import Dict, Any


class FilesService:
    def parse_file(self, filename: str, content: bytes) -> pd.DataFrame:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content), header=None)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl", header=None)
        else:
            raise ValueError("Unsupported file type")

        return self.clean_up(df)

    def clean_up(self, df: pd.DataFrame) -> pd.DataFrame:
        # Drop fully empty rows
        df.dropna(how="all", inplace=True)

        # Try to detect header row
        header_row = self.get_header_row_index(df)

        # Apply header row
        df.columns = self._clean_column_names(df.iloc[header_row])

        # Keep only the data rows after the header
        df = df.iloc[header_row + 1:].reset_index(drop=True)

        # Replace NaN with None (for clean JSON export)
        df = df.where(pd.notnull(df), None)

        return df

    def get_header_row_index(self, df: pd.DataFrame) -> int:
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            filled_strings = row.apply(lambda x: isinstance(x, str) and x.strip() != "")
            ratio = filled_strings.sum() / len(row)

            if ratio >= 0.75:
                return i
        return 0  # fallback

    def _clean_column_names(self, columns: pd.Series) -> list[str]:
        return [
            str(col).strip().lower().replace(" ", "_").replace("-", "_")
            for col in columns
        ]

    def convert_rows_to_dict(self, df: pd.DataFrame) -> list[Dict[str, Any]]:
        formatted_rows = df.to_dict(orient="records")
        return formatted_rows
