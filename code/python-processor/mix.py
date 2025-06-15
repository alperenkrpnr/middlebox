import pandas as pd
import random

covert_df = pd.read_csv("features_covert.csv")
normal_df = pd.read_csv("features_normal.csv")

min_len = min(len(covert_df), len(normal_df))
covert_sample = covert_df.sample(n=min_len, random_state=42)
normal_sample = normal_df.sample(n=min_len, random_state=42)

mixed_df = pd.concat([covert_sample, normal_sample]).sample(frac=1, random_state=42).reset_index(drop=True)

mixed_df.to_csv("features_mixed.csv", index=False)

print(f"Mixed dataset created with {len(mixed_df)} entries → features_mixed.csv")
