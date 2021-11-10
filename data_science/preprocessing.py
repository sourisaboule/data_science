import pandas
from sklearn.base import TransformerMixin, BaseEstimator
from warnings import warn

class DfEncoderOneHot(TransformerMixin, BaseEstimator):
    '''Encoding class. Work only for pandas DataFrame.
     Encoding with 0 and 1 all categorical columns with only 2 classes and 
     do a one hot encoding with the other categorical columns.
     Compatible with sklearn pipelines.'''
    def __init__(self, return_array=False):
        self.return_array = return_array
        self.initialisation()

    def initialisation(self):
        self.original_categorical_columns = []
        self.binary_columns = {}
        self.other_categorical_columns = {}
        self.original_columns = None
        self.encoded_columns = []

    def fit(self, df, y=None):

        self.original_columns = list(df.columns)

        self.original_categorical_columns += list(df.select_dtypes('object')) + list(df.select_dtypes('category')) + list(df.select_dtypes('bool'))

        for col in self.original_categorical_columns:
            classes = list(df[col].dropna().unique())
            if len(classes) == 2:
                if df[col].dtype == 'bool':
                    code = {False: 0.0, True: 1.0}
                else:
                    code = {classes[0]: 0.0, classes[1]: 1.0}
                self.binary_columns[col] = code
            else:
                self.other_categorical_columns[col] = classes

        for i, col in enumerate(self.original_columns):
            if col not in self.other_categorical_columns:
                self.encoded_columns.append(col)
            else:
                for c in self.other_categorical_columns[col]:
                    self.encoded_columns.append(f'{col}_{c}') 
              
        return self

    def transform(self, df):
        df_encoded = df.copy()
        for col, code in self.binary_columns.items():
            for c in df_encoded[col].dropna().unique():
                if c not in code:
                    warn(f'It seems that there is more than 2 categories ({c}) in {col} which was considered a binary column in the fit.\n\
                    this new category will be replaced with 0.0')
                    code[c] = 0.0
                    self.binary_columns[col][c] = 0.0
            df_encoded[col].replace(code, inplace=True)

        for col, classes in self.other_categorical_columns.items():
            for c in classes:
                df_encoded[f'{col}_{c}'] = (df[col] == c).astype('float')

            del df_encoded[col]

        df_encoded.columns = self.encoded_columns

        if self.return_array:
            df_encoded = df_encoded.values

        return df_encoded


    def get_binary_columns(self):
        return self.binary_columns

    def get_other_categorical_columns(self):
        return self.other_categorical_columns

    def get_original_categorical_columns(self):
        return self.original_categorical_columns

    def get_original_columns(self):
        return self.original_columns

    def get_encoded_columns(self):
        return self.encoded_columns

    def __repr__(self):
        return f"{self.__class__.__name__}(return_array={self.return_array})"