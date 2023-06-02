
from googleapiclient.errors import HttpError
from views.utils import clean_df
import pandas as pd
import numpy as np
from services.database import Database


def get_data(username, service, spreadsheetId):

    # Rangos para cada página del excel
    MASTER_SCHEMA = {"expense_projection": {"RANGE": "A2:B100", "FIELDS": ["concepto", "importe"]},
              "income_projection":  {"RANGE": "C2:D100", "FIELDS": ["concepto", "importe"]},
              "expense":  {"RANGE": "E2:G100", "FIELDS": ["concepto", "importe","subconcepto"]},
              "income":  {"RANGE": "H2:J100", "FIELDS": ["concepto", "importe","subconcepto"]},
              "saving_projection":  {"RANGE": "K2:K3", "FIELDS": ["prevision"]}
              }

    MONTHS = {"ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE":10, "NOVIEMBRE": 11, "DICIEMBRE": 12}
    
    #Descargamos e insertamos en base de datos toda la información de cada página. 
    for month, month_number in MONTHS.items():
        for table, config in MASTER_SCHEMA.items():
            try:

                #llamada a la API
                sheet = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheetId,
                                            range=f"{month}!{config.get('RANGE')}", majorDimension="COLUMNS").execute()
                
                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return


                #procesamos los datos
                data = []
                for row in values:
                    data.append(row)

                df = (   
                    pd.DataFrame(data).T
                    .replace("", None)
                    .dropna(how="all"))
                

                df = (
                    df.rename(columns=df.iloc[0])
                    .drop(0)
                    )

                df2 = clean_df(username, df, config["FIELDS"], month_number)

                #se envían a postgres
                with Database() as db:
                    db.insert_fields(df2, username, table, month_number)
         
            except HttpError as err:
                print(err)
