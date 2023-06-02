
def clean_df(username, df, fields, month):
    df.columns = [column.lower() for column in df.columns]
    our_columns = ["username"] + fields + ["month"]
    df = df.assign(username = username)
    df = df.assign(month = month)
    df = df[our_columns]
    return df.values