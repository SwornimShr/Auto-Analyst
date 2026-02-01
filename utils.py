import pandas as pd
import streamlit as st
from typing import Optional


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to make them easier to work with.
    Strips whitespace, converts to lowercase, replaces spaces with underscores.
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


def load_csv_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Load CSV file with multiple encoding attempts.
    Returns normalized dataframe or None if loading fails.
    """
    if uploaded_file is None:
        return None
    
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            uploaded_file.seek(0)  # Reset file pointer
            df = pd.read_csv(uploaded_file, encoding=encoding)
            
            # normalize the column names
            df = normalize_column_names(df)
            
            return df
            
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error reading CSV with {encoding}: {str(e)}")
            continue
    
    return None


def get_dataframe_summary(df: pd.DataFrame) -> dict:
    """
    Generate basic statistics and info about the dataframe.
    """
    summary = {
        'num_rows': len(df),
        'num_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
    }
    
    return summary


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Check if dataframe is valid for analysis.
    Returns (is_valid, error_message)
    """
    if df is None:
        return False, "Dataframe is None"
    
    if df.empty:
        return False, "Dataframe is empty"
    
    if len(df.columns) == 0:
        return False, "No columns found"
    
    # handles the weird edge case where all values are null
    if df.isnull().all().all():
        return False, "All values are null"
    
    return True, ""
