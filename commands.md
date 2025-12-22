
# premiere collect
  python -m collect_data.collector \
  --match-id 2025-11-05_mancity_dortmund \
  --lang de


python collect_data/get_latest_tweet_id.py collect_data/data/2025-11-05_mancity_dortmund_de_full.csv


# next collects
python -m collect_data.collector \
  --match-id 2025-11-05_mancity_dortmund \
  --lang de \
  --since-id 1986923455426510928



