import pandas as pd
import glob
import os

def merge_everything():
    print("🌪️ Fusion de TOUS les fichiers (Binôme + Kaggle)...")
    
    # On prend tous les CSV dans le dossier standardisé
    all_files = glob.glob("collect_data/data/standardized_match_data/*.csv")
    
    # On ajoute aussi le fichier original du binôme s'il est ailleurs
    # all_files.append("collected_data.csv") 
    
    df_list = []
    
    for filename in all_files:
        print(f"   ➕ Ajout de {filename}")
        df = pd.read_csv(filename)
        df_list.append(df)
        
    # Fusion
    final_df = pd.concat(df_list, ignore_index=True)
    
    # Sauvegarde
    output_path = "collect_data/data/DATASET_FINAL_COMPLET.csv"
    final_df.to_csv(output_path, index=False)
    
    print(f"\n🎉 TERMINÉ ! Le fichier final contient {len(final_df)} tweets.")
    print(f"📂 Il est sauvegardé ici : {output_path}")

if __name__ == "__main__":
    merge_everything()