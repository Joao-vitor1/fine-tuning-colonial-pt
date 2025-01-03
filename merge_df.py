import pandas as pd

df = pd.read_csv("textos_medievais.csv")
df_faltantes = pd.read_csv("textos_faltantes.csv")

combined_df = pd.concat([df, df_faltantes], ignore_index=True).fillna(pd.NA)
combined_df.to_csv("textos_medievais_final.csv", index=False, encoding="utf-8")
print(df)
print(df_faltantes)
print(combined_df)