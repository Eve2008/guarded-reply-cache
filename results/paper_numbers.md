# Numbers quoted in the paper

Criteria: `intent` (a hit is correct when the two requests have the same intent) and `strict` (same intent and same slots). All rates are per query of the test split unless marked.

## Data, setup and tuning (Sections 3-5)

- Deployed Persian filler words: 42; deployed critical lexicon: 41; English filler words: 27
- Persian: 16521 utterances, 18 scenarios, 60 intents, partitions {'train': 11514, 'test': 2974, 'dev': 2033}; pool 10863, queries 2974; reusable (strict) 55.9%, same-intent entry exists 100.0%; induced lexicon 4113 words (k=5, c=3, r=0.9); frequency lexicon 4914 words (df<=20); open-ended test queries 11.3%
- English: 16521 utterances, 18 scenarios, 60 intents, partitions {'train': 11514, 'test': 2974, 'dev': 2033}; pool 10937, queries 2974; reusable (strict) 54.1%, same-intent entry exists 100.0%; induced lexicon 4122 words (k=5, c=3, r=0.9); frequency lexicon 4799 words (df<=20); open-ended test queries 11.3%
- Lexicon tuning (fa dev, objective = mean safe-hit rate at 1% intent budget over tri+ind and minilm+ind): best 0.1697 at k=5.0, c=2.0, r=0.9 (lexicon 4113.0)
  - k=5 (max over c): r=0.7: 0.1050, r=0.8: 0.1380, r=0.9: 0.1697, r=0.95: 0.1473, r=1.0: 0.1567
  - k=10 (max over c): r=0.7: 0.0920, r=0.8: 0.1227, r=0.9: 0.1687, r=0.95: 0.1572, r=1.0: 0.1574
  - k=20 (max over c): r=0.7: 0.0890, r=0.8: 0.0981, r=0.9: 0.1606, r=0.95: 0.1586, r=1.0: 0.1579
  - at k=5.0, r=0.9: objective per c c=2: 0.1697 (lexicon 4113), c=3: 0.1697 (lexicon 4113), c=5: 0.1697 (lexicon 4113), c=10: 0.1655 (lexicon 1919)
- Frequency-only lexicon (fa dev): best objective 0.1849 at df<=20.0 (lexicon 4914.0); strict objective there 0.1075; induced lexicon strict objective 0.1225
- Induction from intent labels (fa dev, c=3): best objective 0.1751 at k=20, r=0.7 (lexicon 1771); strict objective 0.1038
- Intent classifier test accuracy, Persian: tri 0.843 (C=10); minilm 0.813 (C=10); mpnet 0.841 (C=10); e5 0.855 (C=10); bgem3 0.873 (C=10)
- Intent classifier test accuracy, English: tri 0.839 (C=10); minilm 0.853 (C=10); mpnet 0.869 (C=10); e5 0.879 (C=10); bgem3 0.882 (C=10)

## Exact-match references (Section 5.2)

| Language | Reference | hit rate % | intent-wrong hits | share of hits % | strict-wrong hits | share % |
|---|---|---|---|---|---|---|
| Persian | exact_norm | 6.2 | 13 | 7.1 | 28 | 15.2 |
| Persian | exact_canon | 8.6 | 18 | 7.0 | 38 | 14.8 |
| English | exact_norm | 0.9 | 1 | 3.7 | 1 | 3.7 |
| English | exact_canon | 8.7 | 3 | 1.2 | 12 | 4.6 |

## Table 1: default thresholds, test

| Language | Policy | tau | safe intent | unsafe intent | safe strict | unsafe strict | opposite | opposite identical/exact-key |
|---|---|---|---|---|---|---|---|---|
| Persian | tri | 0.8 | 10.8 | 0.6 | 9.3 | 2.2 | 1 | 0/1 |
| Persian | minilm | 0.7 | 69.4 | 20.3 | 32.7 | 57.0 | 18 | 0/0 |
| Persian | minilm | 0.8 | 57.7 | 12.0 | 30.8 | 39.0 | 15 | 0/0 |
| Persian | minilm | 0.9 | 34.0 | 4.2 | 22.5 | 15.8 | 5 | 0/0 |
| Persian | mpnet | 0.7 | 72.6 | 19.2 | 35.8 | 56.0 | 6 | 0/0 |
| Persian | mpnet | 0.8 | 63.0 | 12.6 | 34.2 | 41.4 | 6 | 0/0 |
| Persian | mpnet | 0.9 | 38.8 | 4.2 | 25.8 | 17.2 | 1 | 0/0 |
| Persian | e5 | 0.7 | 76.8 | 23.2 | 35.1 | 64.9 | 20 | 0/0 |
| Persian | e5 | 0.8 | 76.8 | 23.2 | 35.1 | 64.9 | 20 | 0/0 |
| Persian | e5 | 0.9 | 73.1 | 18.3 | 34.8 | 56.6 | 19 | 0/0 |
| Persian | bgem3 | 0.7 | 76.3 | 14.5 | 37.4 | 53.3 | 15 | 0/1 |
| Persian | bgem3 | 0.8 | 62.9 | 8.6 | 35.3 | 36.1 | 10 | 0/1 |
| Persian | bgem3 | 0.9 | 33.4 | 2.1 | 24.7 | 10.8 | 1 | 0/1 |
| English | tri | 0.8 | 12.8 | 0.2 | 11.5 | 1.5 | 0 | 0/0 |
| English | minilm | 0.7 | 69.3 | 11.6 | 38.6 | 42.3 | 15 | 0/0 |
| English | minilm | 0.8 | 55.1 | 5.6 | 34.9 | 25.9 | 13 | 0/0 |
| English | minilm | 0.9 | 30.4 | 1.2 | 23.1 | 8.6 | 3 | 0/0 |
| English | mpnet | 0.7 | 71.1 | 12.8 | 38.7 | 45.3 | 10 | 0/0 |
| English | mpnet | 0.8 | 58.1 | 6.6 | 35.7 | 29.0 | 8 | 0/0 |
| English | mpnet | 0.9 | 33.5 | 1.6 | 25.0 | 10.2 | 0 | 0/0 |
| English | e5 | 0.7 | 80.4 | 19.6 | 39.2 | 60.8 | 19 | 0/0 |
| English | e5 | 0.8 | 80.4 | 19.6 | 39.2 | 60.8 | 19 | 0/0 |
| English | e5 | 0.9 | 67.2 | 11.0 | 37.7 | 40.6 | 13 | 0/0 |
| English | bgem3 | 0.7 | 77.8 | 13.9 | 39.8 | 51.8 | 7 | 0/0 |
| English | bgem3 | 0.8 | 65.2 | 7.6 | 37.9 | 34.9 | 2 | 0/0 |
| English | bgem3 | 0.9 | 35.4 | 2.1 | 26.3 | 11.3 | 0 | 0/0 |

- tau 0.7, Persian: unsafe intent 14.5-23.2%, unsafe strict 53.3-64.9%, intent precision 0.768-0.841
- tau 0.7, English: unsafe intent 11.6-19.6%, unsafe strict 42.3-60.8%, intent precision 0.804-0.856
- tau 0.8, Persian: unsafe intent 8.6-23.2%, unsafe strict 36.1-64.9%, intent precision 0.768-0.880
- tau 0.8, English: unsafe intent 5.6-19.6%, unsafe strict 25.9-60.8%, intent precision 0.804-0.908
- tau 0.9, Persian: unsafe intent 2.1-18.3%, unsafe strict 10.8-56.6%, intent precision 0.800-0.940
- tau 0.9, English: unsafe intent 1.2-11.0%, unsafe strict 8.6-40.6%, intent precision 0.859-0.961
- Persian minilm: 0.8 -> 0.9 cuts unsafe intent 2.84x
- Persian mpnet: 0.8 -> 0.9 cuts unsafe intent 2.97x
- Persian e5: 0.8 -> 0.9 cuts unsafe intent 1.27x
- Persian bgem3: 0.8 -> 0.9 cuts unsafe intent 4.05x
- English minilm: 0.8 -> 0.9 cuts unsafe intent 4.49x
- English mpnet: 0.8 -> 0.9 cuts unsafe intent 3.98x
- English e5: 0.8 -> 0.9 cuts unsafe intent 1.78x
- English bgem3: 0.8 -> 0.9 cuts unsafe intent 3.60x

## Error types of wrong hits at default 0.8, test (Section 6.1)

### Persian, intent criterion

| method | info_vs_info | opposite_action | other_state_change | state_change_vs_info | total | identical |
|---|---|---|---|---|---|---|
| tri | 2 | 1 | 13 | 3 | 19 | 13 |
| minilm | 96 | 15 | 126 | 121 | 358 | 13 |
| mpnet | 118 | 6 | 123 | 127 | 374 | 13 |
| e5 | 279 | 20 | 187 | 204 | 690 | 13 |
| bgem3 | 66 | 10 | 104 | 75 | 255 | 13 |

Shares over the five policies: info_vs_info 33.1%, opposite_action 3.1%, other_state_change 32.6%, state_change_vs_info 31.2%

### English, intent criterion

| method | info_vs_info | opposite_action | other_state_change | state_change_vs_info | total | identical |
|---|---|---|---|---|---|---|
| tri | 1 | 0 | 1 | 3 | 5 | 1 |
| minilm | 55 | 13 | 38 | 60 | 166 | 1 |
| mpnet | 71 | 8 | 42 | 74 | 195 | 1 |
| e5 | 254 | 19 | 147 | 164 | 584 | 1 |
| bgem3 | 82 | 2 | 82 | 61 | 227 | 1 |

Shares over the five policies: info_vs_info 39.3%, opposite_action 3.6%, other_state_change 26.3%, state_change_vs_info 30.8%

### Persian, strict criterion

| method | argument_info | argument_state_change | info_vs_info | opposite_action | other_open_question | other_state_change | state_change_vs_info | total | identical |
|---|---|---|---|---|---|---|---|---|---|
| tri | 17 | 24 | 2 | 1 | 4 | 13 | 3 | 64 | 28 |
| minilm | 353 | 380 | 96 | 15 | 69 | 126 | 121 | 1160 | 28 |
| mpnet | 385 | 390 | 118 | 6 | 82 | 123 | 127 | 1231 | 28 |
| e5 | 512 | 562 | 279 | 20 | 166 | 187 | 204 | 1930 | 28 |
| bgem3 | 338 | 422 | 66 | 10 | 60 | 104 | 75 | 1075 | 28 |

Shares over the five policies: argument_info 29.4%, argument_state_change 32.6%, info_vs_info 10.3%, opposite_action 1.0%, other_open_question 7.0%, other_state_change 10.1%, state_change_vs_info 9.7%

### English, strict criterion

| method | argument_info | argument_state_change | info_vs_info | opposite_action | other_open_question | other_state_change | state_change_vs_info | total | identical |
|---|---|---|---|---|---|---|---|---|---|
| tri | 21 | 15 | 1 | 0 | 3 | 1 | 3 | 44 | 1 |
| minilm | 248 | 299 | 55 | 13 | 56 | 38 | 60 | 769 | 1 |
| mpnet | 286 | 314 | 71 | 8 | 66 | 42 | 74 | 861 | 1 |
| e5 | 485 | 558 | 254 | 19 | 181 | 147 | 164 | 1808 | 1 |
| bgem3 | 325 | 420 | 82 | 2 | 67 | 82 | 61 | 1039 | 1 |

Shares over the five policies: argument_info 30.2%, argument_state_change 35.5%, info_vs_info 10.2%, opposite_action 0.9%, other_open_question 8.3%, other_state_change 6.9%, state_change_vs_info 8.0%

## Guards and gates at default thresholds (Table 2)

| Language | Candidate | point | intent: unsafe plain->cand (ratio, CI excl 0) | safe plain->cand (ratio) | strict: unsafe plain->cand (ratio, CI excl 0) | safe plain->cand |
|---|---|---|---|---|---|---|
| Persian | tri+ind | default 0.8 | 0.6->0.6 (1.00x, False) | 10.8->10.0 (1.08x) | 2.2->1.5 (1.39x, True) | 9.3->9.1 |
| Persian | tri+freq | default 0.8 | 0.6->0.6 (1.00x, False) | 10.8->10.3 (1.05x) | 2.2->1.9 (1.12x, True) | 9.3->9.0 |
| Persian | tri+dep | default 0.8 | 0.6->0.6 (1.00x, False) | 10.8->10.7 (1.02x) | 2.2->2.1 (1.05x, False) | 9.3->9.2 |
| Persian | tri+indv | default 0.8 | 0.6->0.6 (1.00x, False) | 10.8->10.0 (1.08x) | 2.2->1.5 (1.39x, True) | 9.3->9.1 |
| Persian | tri+gate | default 0.8 | 0.6->0.6 (1.00x, False) | 10.8->10.8 (1.01x) | 2.2->2.2 (1.00x, False) | 9.3->9.2 |
| Persian | tri+gate+ind | default 0.8 | 0.6->0.6 (1.00x, False) | 10.8->10.0 (1.08x) | 2.2->1.5 (1.39x, True) | 9.3->9.1 |
| Persian | minilm+ind | default 0.8 | 12.0->5.3 (2.27x, True) | 57.7->32.8 (1.76x) | 39.0->10.8 (3.60x, True) | 30.8->27.2 |
| Persian | minilm+ind | default 0.9 | 4.2->2.4 (1.80x, True) | 34.0->22.8 (1.49x) | 15.8->5.4 (2.91x, True) | 22.5->19.8 |
| Persian | minilm+freq | default 0.8 | 12.0->6.2 (1.94x, True) | 57.7->37.1 (1.56x) | 39.0->18.9 (2.06x, True) | 30.8->24.4 |
| Persian | minilm+freq | default 0.9 | 4.2->2.7 (1.57x, True) | 34.0->23.9 (1.42x) | 15.8->8.2 (1.92x, True) | 22.5->18.4 |
| Persian | minilm+dep | default 0.8 | 12.0->10.5 (1.15x, True) | 57.7->51.5 (1.12x) | 39.0->32.3 (1.21x, True) | 30.8->29.7 |
| Persian | minilm+dep | default 0.9 | 4.2->3.8 (1.11x, True) | 34.0->30.7 (1.11x) | 15.8->13.1 (1.21x, True) | 22.5->21.4 |
| Persian | minilm+indv | default 0.8 | 12.0->3.2 (3.73x, True) | 57.7->26.2 (2.20x) | 39.0->6.8 (5.71x, True) | 30.8->22.6 |
| Persian | minilm+indv | default 0.9 | 4.2->1.9 (2.21x, True) | 34.0->20.5 (1.65x) | 15.8->4.4 (3.55x, True) | 22.5->18.0 |
| Persian | minilm+gate | default 0.8 | 12.0->5.9 (2.06x, True) | 57.7->59.3 (0.97x) | 39.0->34.5 (1.13x, True) | 30.8->30.6 |
| Persian | minilm+gate | default 0.9 | 4.2->2.0 (2.17x, True) | 34.0->34.2 (1.00x) | 15.8->13.5 (1.17x, True) | 22.5->22.6 |
| Persian | minilm+gate+ind | default 0.8 | 12.0->2.1 (5.68x, True) | 57.7->33.0 (1.75x) | 39.0->7.8 (5.02x, True) | 30.8->27.3 |
| Persian | minilm+gate+ind | default 0.9 | 4.2->1.0 (4.06x, True) | 34.0->23.1 (1.47x) | 15.8->4.1 (3.81x, True) | 22.5->20.0 |
| Persian | mpnet+ind | default 0.8 | 12.6->4.7 (2.67x, True) | 63.0->35.1 (1.80x) | 41.4->10.3 (4.02x, True) | 34.2->29.5 |
| Persian | mpnet+ind | default 0.9 | 4.2->2.0 (2.17x, True) | 38.8->25.6 (1.51x) | 17.2->5.4 (3.20x, True) | 25.8->22.2 |
| Persian | mpnet+freq | default 0.8 | 12.6->6.3 (1.99x, True) | 63.0->39.4 (1.60x) | 41.4->19.4 (2.13x, True) | 34.2->26.3 |
| Persian | mpnet+freq | default 0.9 | 4.2->2.2 (1.94x, True) | 38.8->26.7 (1.45x) | 17.2->8.4 (2.04x, True) | 25.8->20.4 |
| Persian | mpnet+dep | default 0.8 | 12.6->10.7 (1.17x, True) | 63.0->56.7 (1.11x) | 41.4->33.9 (1.22x, True) | 34.2->33.5 |
| Persian | mpnet+dep | default 0.9 | 4.2->3.5 (1.22x, True) | 38.8->35.1 (1.11x) | 17.2->13.7 (1.26x, True) | 25.8->24.9 |
| Persian | mpnet+indv | default 0.8 | 12.6->3.0 (4.20x, True) | 63.0->28.1 (2.24x) | 41.4->6.8 (6.09x, True) | 34.2->24.3 |
| Persian | mpnet+indv | default 0.9 | 4.2->1.5 (2.80x, True) | 38.8->22.6 (1.72x) | 17.2->4.1 (4.16x, True) | 25.8->19.9 |
| Persian | mpnet+gate | default 0.8 | 12.6->6.4 (1.98x, True) | 63.0->64.9 (0.97x) | 41.4->37.1 (1.12x, True) | 34.2->34.2 |
| Persian | mpnet+gate | default 0.9 | 4.2->2.6 (1.66x, True) | 38.8->38.6 (1.00x) | 17.2->15.8 (1.09x, True) | 25.8->25.4 |
| Persian | mpnet+gate+ind | default 0.8 | 12.6->2.3 (5.42x, True) | 63.0->35.1 (1.80x) | 41.4->8.0 (5.15x, True) | 34.2->29.4 |
| Persian | mpnet+gate+ind | default 0.9 | 4.2->1.2 (3.50x, True) | 38.8->25.6 (1.52x) | 17.2->4.7 (3.63x, True) | 25.8->22.0 |
| Persian | e5+ind | default 0.8 | 23.2->13.0 (1.78x, True) | 76.8->39.0 (1.97x) | 64.9->21.1 (3.08x, True) | 35.1->30.9 |
| Persian | e5+ind | default 0.9 | 18.3->8.9 (2.06x, True) | 73.1->37.8 (1.94x) | 56.6->16.1 (3.52x, True) | 34.8->30.6 |
| Persian | e5+freq | default 0.8 | 23.2->18.3 (1.27x, True) | 76.8->47.6 (1.61x) | 64.9->38.6 (1.68x, True) | 35.1->27.3 |
| Persian | e5+freq | default 0.9 | 18.3->11.0 (1.67x, True) | 73.1->45.7 (1.60x) | 56.6->29.6 (1.91x, True) | 34.8->27.0 |
| Persian | e5+dep | default 0.8 | 23.2->26.8 (0.87x, True) | 76.8->72.3 (1.06x) | 64.9->64.5 (1.01x, False) | 35.1->34.5 |
| Persian | e5+dep | default 0.9 | 18.3->18.9 (0.97x, False) | 73.1->67.5 (1.08x) | 56.6->52.2 (1.08x, True) | 34.8->34.2 |
| Persian | e5+indv | default 0.8 | 23.2->4.4 (5.27x, True) | 76.8->29.0 (2.65x) | 64.9->8.7 (7.42x, True) | 35.1->24.7 |
| Persian | e5+indv | default 0.9 | 18.3->4.2 (4.40x, True) | 73.1->28.9 (2.53x) | 56.6->8.4 (6.71x, True) | 34.8->24.6 |
| Persian | e5+gate | default 0.8 | 23.2->14.7 (1.58x, True) | 76.8->85.3 (0.90x) | 64.9->63.5 (1.02x, True) | 35.1->36.5 |
| Persian | e5+gate | default 0.9 | 18.3->9.8 (1.87x, True) | 73.1->78.4 (0.93x) | 56.6->52.0 (1.09x, True) | 34.8->36.2 |
| Persian | e5+gate+ind | default 0.8 | 23.2->4.4 (5.27x, True) | 76.8->41.8 (1.84x) | 64.9->13.9 (4.67x, True) | 35.1->32.3 |
| Persian | e5+gate+ind | default 0.9 | 18.3->3.2 (5.80x, True) | 73.1->39.2 (1.87x) | 56.6->10.8 (5.25x, True) | 34.8->31.6 |
| Persian | bgem3+ind | default 0.8 | 8.6->5.0 (1.72x, True) | 62.9->34.9 (1.80x) | 36.1->10.6 (3.41x, True) | 35.3->29.3 |
| Persian | bgem3+ind | default 0.9 | 2.1->1.5 (1.43x, True) | 33.4->23.8 (1.40x) | 10.8->4.2 (2.54x, True) | 24.7->21.0 |
| Persian | bgem3+freq | default 0.8 | 8.6->5.4 (1.58x, True) | 62.9->41.1 (1.53x) | 36.1->19.8 (1.83x, True) | 35.3->26.8 |
| Persian | bgem3+freq | default 0.9 | 2.1->1.6 (1.34x, True) | 33.4->25.3 (1.32x) | 10.8->6.9 (1.55x, True) | 24.7->19.9 |
| Persian | bgem3+dep | default 0.8 | 8.6->8.0 (1.07x, False) | 62.9->56.6 (1.11x) | 36.1->29.9 (1.21x, True) | 35.3->34.7 |
| Persian | bgem3+dep | default 0.9 | 2.1->1.8 (1.19x, True) | 33.4->30.6 (1.09x) | 10.8->8.4 (1.29x, True) | 24.7->24.0 |
| Persian | bgem3+indv | default 0.8 | 8.6->3.1 (2.80x, True) | 62.9->29.3 (2.15x) | 36.1->7.3 (4.95x, True) | 35.3->25.0 |
| Persian | bgem3+indv | default 0.9 | 2.1->1.1 (1.85x, True) | 33.4->22.3 (1.50x) | 10.8->3.6 (3.02x, True) | 24.7->19.9 |
| Persian | bgem3+gate | default 0.8 | 8.6->4.1 (2.07x, True) | 62.9->64.5 (0.98x) | 36.1->33.0 (1.10x, True) | 35.3->35.6 |
| Persian | bgem3+gate | default 0.9 | 2.1->1.0 (2.10x, True) | 33.4->33.4 (1.00x) | 10.8->9.7 (1.11x, True) | 24.7->24.7 |
| Persian | bgem3+gate+ind | default 0.8 | 8.6->2.1 (4.11x, True) | 62.9->35.6 (1.77x) | 36.1->8.0 (4.54x, True) | 35.3->29.8 |
| Persian | bgem3+gate+ind | default 0.9 | 2.1->0.8 (2.74x, True) | 33.4->23.9 (1.40x) | 10.8->3.5 (3.05x, True) | 24.7->21.1 |
| Persian | minilmft+ind | default 0.8 | 26.3->10.1 (2.59x, True) | 68.0->38.4 (1.77x) | 54.7->17.1 (3.19x, True) | 39.5->31.4 |
| Persian | minilmft+ind | default 0.9 | 14.6->6.7 (2.17x, True) | 57.1->36.1 (1.58x) | 33.7->12.5 (2.70x, True) | 37.9->30.3 |
| Persian | minilmft+freq | default 0.8 | 26.3->12.4 (2.11x, True) | 68.0->43.0 (1.58x) | 54.7->25.8 (2.12x, True) | 39.5->29.7 |
| Persian | minilmft+freq | default 0.9 | 14.6->7.8 (1.87x, True) | 57.1->36.9 (1.55x) | 33.7->16.1 (2.09x, True) | 37.9->28.6 |
| Persian | minilmft+dep | default 0.8 | 26.3->23.8 (1.10x, True) | 68.0->64.7 (1.05x) | 54.7->50.7 (1.08x, True) | 39.5->37.8 |
| Persian | minilmft+dep | default 0.9 | 14.6->12.2 (1.19x, True) | 57.1->52.6 (1.08x) | 33.7->28.9 (1.17x, True) | 37.9->35.9 |
| Persian | minilmft+indv | default 0.8 | 26.3->5.4 (4.82x, True) | 68.0->32.4 (2.10x) | 54.7->10.3 (5.30x, True) | 39.5->27.5 |
| Persian | minilmft+indv | default 0.9 | 14.6->4.8 (3.05x, True) | 57.1->31.6 (1.80x) | 33.7->9.4 (3.59x, True) | 37.9->27.0 |
| English | tri+ind | default 0.8 | 0.2->0.2 (1.00x, False) | 12.8->11.7 (1.09x) | 1.5->0.8 (1.91x, True) | 11.5->11.1 |
| English | tri+freq | default 0.8 | 0.2->0.2 (1.00x, False) | 12.8->12.1 (1.06x) | 1.5->1.0 (1.42x, True) | 11.5->11.2 |
| English | tri+indv | default 0.8 | 0.2->0.2 (1.00x, False) | 12.8->11.7 (1.09x) | 1.5->0.8 (1.91x, True) | 11.5->11.1 |
| English | tri+gate | default 0.8 | 0.2->0.1 (1.25x, False) | 12.8->12.7 (1.00x) | 1.5->1.4 (1.05x, False) | 11.5->11.5 |
| English | tri+gate+ind | default 0.8 | 0.2->0.1 (1.25x, False) | 12.8->11.7 (1.09x) | 1.5->0.7 (2.00x, True) | 11.5->11.1 |
| English | minilm+ind | default 0.8 | 5.6->3.4 (1.64x, True) | 55.1->35.5 (1.55x) | 25.9->7.6 (3.39x, True) | 34.9->31.3 |
| English | minilm+ind | default 0.9 | 1.2->1.0 (1.28x, False) | 30.4->23.7 (1.28x) | 8.6->3.4 (2.52x, True) | 23.1->21.3 |
| English | minilm+freq | default 0.8 | 5.6->3.8 (1.47x, True) | 55.1->39.0 (1.42x) | 25.9->14.4 (1.80x, True) | 34.9->28.4 |
| English | minilm+freq | default 0.9 | 1.2->1.0 (1.28x, True) | 30.4->25.2 (1.21x) | 8.6->5.9 (1.45x, True) | 23.1->20.2 |
| English | minilm+indv | default 0.8 | 5.6->2.7 (2.08x, True) | 55.1->31.7 (1.74x) | 25.9->6.1 (4.27x, True) | 34.9->28.3 |
| English | minilm+indv | default 0.9 | 1.2->0.8 (1.54x, True) | 30.4->22.6 (1.35x) | 8.6->3.0 (2.90x, True) | 23.1->20.4 |
| English | minilm+gate | default 0.8 | 5.6->2.3 (2.41x, True) | 55.1->55.1 (1.00x) | 25.9->23.0 (1.12x, True) | 34.9->34.4 |
| English | minilm+gate | default 0.9 | 1.2->0.6 (1.95x, True) | 30.4->30.0 (1.01x) | 8.6->8.0 (1.08x, True) | 23.1->22.7 |
| English | minilm+gate+ind | default 0.8 | 5.6->1.2 (4.49x, True) | 55.1->35.3 (1.56x) | 25.9->5.5 (4.72x, True) | 34.9->31.1 |
| English | minilm+gate+ind | default 0.9 | 1.2->0.4 (3.08x, True) | 30.4->23.4 (1.30x) | 8.6->2.9 (3.00x, True) | 23.1->21.0 |
| English | mpnet+ind | default 0.8 | 6.6->3.7 (1.79x, True) | 58.1->36.3 (1.60x) | 29.0->8.0 (3.62x, True) | 35.7->31.9 |
| English | mpnet+ind | default 0.9 | 1.6->1.1 (1.44x, True) | 33.5->25.2 (1.33x) | 10.2->3.6 (2.82x, True) | 25.0->22.8 |
| English | mpnet+freq | default 0.8 | 6.6->4.8 (1.37x, True) | 58.1->40.6 (1.43x) | 29.0->15.8 (1.83x, True) | 35.7->29.5 |
| English | mpnet+freq | default 0.9 | 1.6->1.2 (1.36x, True) | 33.5->26.6 (1.26x) | 10.2->6.4 (1.60x, True) | 25.0->21.5 |
| English | mpnet+indv | default 0.8 | 6.6->3.0 (2.22x, True) | 58.1->31.6 (1.84x) | 29.0->6.3 (4.60x, True) | 35.7->28.2 |
| English | mpnet+indv | default 0.9 | 1.6->1.1 (1.53x, True) | 33.5->23.5 (1.42x) | 10.2->3.1 (3.28x, True) | 25.0->21.5 |
| English | mpnet+gate | default 0.8 | 6.6->2.9 (2.24x, True) | 58.1->58.7 (0.99x) | 29.0->25.7 (1.13x, True) | 35.7->35.9 |
| English | mpnet+gate | default 0.9 | 1.6->0.8 (2.13x, True) | 33.5->33.5 (1.00x) | 10.2->9.4 (1.08x, True) | 25.0->24.9 |
| English | mpnet+gate+ind | default 0.8 | 6.6->1.4 (4.76x, True) | 58.1->36.6 (1.59x) | 29.0->5.7 (5.06x, True) | 35.7->32.2 |
| English | mpnet+gate+ind | default 0.9 | 1.6->0.5 (3.27x, True) | 33.5->25.0 (1.34x) | 10.2->3.0 (3.43x, True) | 25.0->22.5 |
| English | e5+ind | default 0.8 | 19.6->12.7 (1.55x, True) | 80.4->44.2 (1.82x) | 60.8->21.3 (2.85x, True) | 39.2->35.6 |
| English | e5+ind | default 0.9 | 11.0->5.4 (2.02x, True) | 67.2->39.6 (1.70x) | 40.6->10.8 (3.76x, True) | 37.7->34.3 |
| English | e5+freq | default 0.8 | 19.6->16.8 (1.17x, True) | 80.4->52.9 (1.52x) | 60.8->37.7 (1.61x, True) | 39.2->32.0 |
| English | e5+freq | default 0.9 | 11.0->6.5 (1.69x, True) | 67.2->45.7 (1.47x) | 40.6->21.7 (1.87x, True) | 37.7->30.6 |
| English | e5+indv | default 0.8 | 19.6->5.0 (3.95x, True) | 80.4->33.6 (2.39x) | 60.8->9.3 (6.55x, True) | 39.2->29.3 |
| English | e5+indv | default 0.9 | 11.0->3.8 (2.88x, True) | 67.2->32.4 (2.07x) | 40.6->7.4 (5.46x, True) | 37.7->28.8 |
| English | e5+gate | default 0.8 | 19.6->11.7 (1.67x, True) | 80.4->87.9 (0.91x) | 60.8->59.8 (1.02x, True) | 39.2->39.8 |
| English | e5+gate | default 0.9 | 11.0->4.3 (2.54x, True) | 67.2->69.8 (0.96x) | 40.6->36.0 (1.13x, True) | 37.7->38.1 |
| English | e5+gate+ind | default 0.8 | 19.6->3.7 (5.31x, True) | 80.4->46.5 (1.73x) | 60.8->13.6 (4.46x, True) | 39.2->36.6 |
| English | e5+gate+ind | default 0.9 | 11.0->1.8 (6.07x, True) | 67.2->40.1 (1.68x) | 40.6->7.3 (5.56x, True) | 37.7->34.6 |
| English | bgem3+ind | default 0.8 | 7.6->4.3 (1.76x, True) | 65.2->39.4 (1.66x) | 34.9->9.4 (3.71x, True) | 37.9->34.3 |
| English | bgem3+ind | default 0.9 | 2.1->1.3 (1.62x, True) | 35.4->26.6 (1.33x) | 11.3->3.5 (3.25x, True) | 26.3->24.4 |
| English | bgem3+freq | default 0.8 | 7.6->5.1 (1.49x, True) | 65.2->45.8 (1.43x) | 34.9->20.0 (1.75x, True) | 37.9->30.9 |
| English | bgem3+freq | default 0.9 | 2.1->1.3 (1.62x, True) | 35.4->28.6 (1.24x) | 11.3->7.4 (1.52x, True) | 26.3->22.5 |
| English | bgem3+indv | default 0.8 | 7.6->2.9 (2.64x, True) | 65.2->33.1 (1.97x) | 34.9->6.5 (5.38x, True) | 37.9->29.5 |
| English | bgem3+indv | default 0.9 | 2.1->1.2 (1.80x, True) | 35.4->24.2 (1.46x) | 11.3->2.9 (3.85x, True) | 26.3->22.5 |
| English | bgem3+gate | default 0.8 | 7.6->3.5 (2.16x, True) | 65.2->66.5 (0.98x) | 34.9->31.9 (1.09x, True) | 37.9->38.2 |
| English | bgem3+gate | default 0.9 | 2.1->0.8 (2.52x, True) | 35.4->35.3 (1.00x) | 11.3->10.0 (1.13x, True) | 26.3->26.2 |
| English | bgem3+gate+ind | default 0.8 | 7.6->1.7 (4.45x, True) | 65.2->39.5 (1.65x) | 34.9->6.8 (5.12x, True) | 37.9->34.4 |
| English | bgem3+gate+ind | default 0.9 | 2.1->0.5 (4.20x, True) | 35.4->26.4 (1.34x) | 11.3->2.6 (4.35x, True) | 26.3->24.3 |
| English | minilmft+ind | default 0.8 | 22.4->9.4 (2.37x, True) | 67.1->41.5 (1.62x) | 45.1->15.1 (2.98x, True) | 44.4->35.9 |
| English | minilmft+ind | default 0.9 | 11.6->5.7 (2.01x, True) | 55.5->39.4 (1.41x) | 24.7->10.2 (2.42x, True) | 42.3->34.9 |
| English | minilmft+freq | default 0.8 | 22.4->11.9 (1.88x, True) | 67.1->45.6 (1.47x) | 45.1->22.9 (1.96x, True) | 44.4->34.5 |
| English | minilmft+freq | default 0.9 | 11.6->6.9 (1.68x, True) | 55.5->40.5 (1.37x) | 24.7->13.9 (1.79x, True) | 42.3->33.5 |
| English | minilmft+indv | default 0.8 | 22.4->6.2 (3.59x, True) | 67.1->37.0 (1.82x) | 45.1->10.2 (4.42x, True) | 44.4->33.0 |
| English | minilmft+indv | default 0.9 | 11.6->4.7 (2.44x, True) | 55.5->35.9 (1.55x) | 24.7->8.2 (3.02x, True) | 42.3->32.4 |

- +ind, intent, Persian, encoders at 0.8/0.9: unsafe ratio 1.43-2.67x (removed 30-63%), safe hits removed 29-49%, precision 0.768-0.940 -> 0.749-0.941
- +ind, intent, English, encoders at 0.8/0.9: unsafe ratio 1.28-2.02x (removed 22-51%), safe hits removed 22-45%, precision 0.804-0.961 -> 0.777-0.960
- +ind, strict, Persian, encoders at 0.8/0.9: unsafe ratio 2.54-4.02x (removed 61-75%), safe hits removed 11-17%, precision 0.351-0.697 -> 0.595-0.832
- +ind, strict, English, encoders at 0.8/0.9: unsafe ratio 2.52-3.76x (removed 60-73%), safe hits removed 7-10%, precision 0.392-0.729 -> 0.625-0.876
- +indv, intent, Persian, encoders at 0.8/0.9: unsafe ratio 1.85-5.27x (removed 46-81%), safe hits removed 33-62%, precision 0.768-0.940 -> 0.868-0.951
- +indv, intent, English, encoders at 0.8/0.9: unsafe ratio 1.53-3.95x (removed 35-75%), safe hits removed 26-58%, precision 0.804-0.961 -> 0.871-0.965
- +indv, strict, Persian, encoders at 0.8/0.9: unsafe ratio 3.02-7.42x (removed 67-87%), safe hits removed 20-30%, precision 0.351-0.697 -> 0.738-0.848
- +indv, strict, English, encoders at 0.8/0.9: unsafe ratio 2.90-6.55x (removed 65-85%), safe hits removed 12-25%, precision 0.392-0.729 -> 0.760-0.885
- +gate, intent, Persian, encoders at 0.8/0.9: unsafe ratio 1.58-2.17x (removed 37-54%), safe hits removed -11-0%, precision 0.768-0.940 -> 0.853-0.971
- +gate, intent, English, encoders at 0.8/0.9: unsafe ratio 1.67-2.54x (removed 40-61%), safe hits removed -9-1%, precision 0.804-0.961 -> 0.882-0.979
- +gate, strict, Persian, encoders at 0.8/0.9: unsafe ratio 1.02-1.17x (removed 2-14%), safe hits removed -4-2%, precision 0.351-0.697 -> 0.365-0.719
- +gate, strict, English, encoders at 0.8/0.9: unsafe ratio 1.02-1.13x (removed 2-12%), safe hits removed -2-2%, precision 0.392-0.729 -> 0.400-0.740
- +gate+ind, intent, Persian, encoders at 0.8/0.9: unsafe ratio 2.74-5.80x (removed 63-83%), safe hits removed 28-46%, precision 0.768-0.940 -> 0.905-0.969
- +gate+ind, intent, English, encoders at 0.8/0.9: unsafe ratio 3.08-6.07x (removed 68-84%), safe hits removed 23-42%, precision 0.804-0.961 -> 0.926-0.983
- +gate+ind, strict, Persian, encoders at 0.8/0.9: unsafe ratio 3.05-5.25x (removed 67-81%), safe hits removed 8-16%, precision 0.351-0.697 -> 0.699-0.857
- +gate+ind, strict, English, encoders at 0.8/0.9: unsafe ratio 3.00-5.56x (removed 67-82%), safe hits removed 7-11%, precision 0.392-0.729 -> 0.729-0.904
- +freq, intent, Persian, encoders at 0.8/0.9: unsafe ratio 1.27-1.99x (removed 21-50%), safe hits removed 24-38%, precision 0.768-0.940 -> 0.722-0.941
- +freq, intent, English, encoders at 0.8/0.9: unsafe ratio 1.17-1.69x (removed 14-41%), safe hits removed 17-34%, precision 0.804-0.961 -> 0.758-0.963
- +freq, strict, Persian, encoders at 0.8/0.9: unsafe ratio 1.55-2.13x (removed 36-53%), safe hits removed 18-24%, precision 0.351-0.697 -> 0.414-0.742
- +freq, strict, English, encoders at 0.8/0.9: unsafe ratio 1.45-1.87x (removed 31-47%), safe hits removed 12-19%, precision 0.392-0.729 -> 0.459-0.773
- +dep, intent, Persian, encoders at 0.8/0.9: unsafe ratio 0.87-1.22x (removed -15-18%), safe hits removed 6-11%, precision 0.768-0.940 -> 0.730-0.945
- +dep, strict, Persian, encoders at 0.8/0.9: unsafe ratio 1.01-1.29x (removed 1-22%), safe hits removed 2-5%, precision 0.351-0.697 -> 0.349-0.741

## Pre-filter swaps: wrong hits under the guard whose unguarded hit was correct (Section 6.2)

- Persian tri+ind @ 0.8: wrong-intent hits 19, of which 0 replaced a correct unguarded hit
- Persian tri+gate @ 0.8: wrong-intent hits 19, of which 0 replaced a correct unguarded hit
- Persian minilm+ind @ 0.8: wrong-intent hits 158, of which 28 replaced a correct unguarded hit
- Persian minilm+gate @ 0.8: wrong-intent hits 174, of which 28 replaced a correct unguarded hit
- Persian minilm+ind @ 0.9: wrong-intent hits 70, of which 6 replaced a correct unguarded hit
- Persian minilm+gate @ 0.9: wrong-intent hits 58, of which 3 replaced a correct unguarded hit
- Persian mpnet+ind @ 0.8: wrong-intent hits 140, of which 20 replaced a correct unguarded hit
- Persian mpnet+gate @ 0.8: wrong-intent hits 189, of which 27 replaced a correct unguarded hit
- Persian mpnet+ind @ 0.9: wrong-intent hits 58, of which 7 replaced a correct unguarded hit
- Persian mpnet+gate @ 0.9: wrong-intent hits 76, of which 7 replaced a correct unguarded hit
- Persian e5+ind @ 0.8: wrong-intent hits 388, of which 133 replaced a correct unguarded hit
- Persian e5+gate @ 0.8: wrong-intent hits 438, of which 118 replaced a correct unguarded hit
- Persian e5+ind @ 0.9: wrong-intent hits 265, of which 81 replaced a correct unguarded hit
- Persian e5+gate @ 0.9: wrong-intent hits 292, of which 79 replaced a correct unguarded hit
- Persian bgem3+ind @ 0.8: wrong-intent hits 148, of which 38 replaced a correct unguarded hit
- Persian bgem3+gate @ 0.8: wrong-intent hits 123, of which 24 replaced a correct unguarded hit
- Persian bgem3+ind @ 0.9: wrong-intent hits 44, of which 5 replaced a correct unguarded hit
- Persian bgem3+gate @ 0.9: wrong-intent hits 30, of which 1 replaced a correct unguarded hit
- English tri+ind @ 0.8: wrong-intent hits 5, of which 0 replaced a correct unguarded hit
- English tri+gate @ 0.8: wrong-intent hits 4, of which 0 replaced a correct unguarded hit
- English minilm+ind @ 0.8: wrong-intent hits 101, of which 16 replaced a correct unguarded hit
- English minilm+gate @ 0.8: wrong-intent hits 69, of which 10 replaced a correct unguarded hit
- English minilm+ind @ 0.9: wrong-intent hits 29, of which 5 replaced a correct unguarded hit
- English minilm+gate @ 0.9: wrong-intent hits 19, of which 2 replaced a correct unguarded hit
- English mpnet+ind @ 0.8: wrong-intent hits 109, of which 18 replaced a correct unguarded hit
- English mpnet+gate @ 0.8: wrong-intent hits 87, of which 12 replaced a correct unguarded hit
- English mpnet+ind @ 0.9: wrong-intent hits 34, of which 2 replaced a correct unguarded hit
- English mpnet+gate @ 0.9: wrong-intent hits 23, of which 1 replaced a correct unguarded hit
- English e5+ind @ 0.8: wrong-intent hits 377, of which 143 replaced a correct unguarded hit
- English e5+gate @ 0.8: wrong-intent hits 349, of which 110 replaced a correct unguarded hit
- English e5+ind @ 0.9: wrong-intent hits 162, of which 31 replaced a correct unguarded hit
- English e5+gate @ 0.9: wrong-intent hits 129, of which 31 replaced a correct unguarded hit
- English bgem3+ind @ 0.8: wrong-intent hits 129, of which 27 replaced a correct unguarded hit
- English bgem3+gate @ 0.8: wrong-intent hits 105, of which 21 replaced a correct unguarded hit
- English bgem3+ind @ 0.9: wrong-intent hits 39, of which 3 replaced a correct unguarded hit
- English bgem3+gate @ 0.9: wrong-intent hits 25, of which 1 replaced a correct unguarded hit

## Dev-chosen thresholds: change in safe hits, test (Tables 3-4)

| Language | Candidate | budget | safe plain->cand | d_safe | CI (test bootstrap) | CI (nested) | test unsafe plain/cand |
|---|---|---|---|---|---|---|---|
| Persian | tri+ind | intent 0.01 | 17.6->15.7 | -1.8 | [-2.6, -1.1] | [-4.7, 2.7] | 0.9/0.9 |
| Persian | tri+ind | intent 0.02 | 26.7->23.3 | -3.5 | [-4.5, -2.5] | [-6.6, 0.0] | 2.0/1.8 |
| Persian | tri+freq | intent 0.01 | 17.6->19.2 | +1.6 | [0.8, 2.5] | [-3.2, 4.4] | 0.9/1.1 |
| Persian | tri+freq | intent 0.02 | 26.7->24.4 | -2.4 | [-3.3, -1.5] | [-4.9, 1.0] | 2.0/1.9 |
| Persian | tri+dep | intent 0.01 | 17.6->17.2 | -0.4 | [-0.6, -0.2] | [-0.7, 3.7] | 0.9/0.8 |
| Persian | tri+dep | intent 0.02 | 26.7->27.1 | +0.4 | [-0.2, 1.0] | [-1.6, 3.3] | 2.0/2.0 |
| Persian | tri+indv | intent 0.01 | 17.6->17.1 | -0.5 | [-1.4, 0.5] | [-5.0, 3.0] | 0.9/1.0 |
| Persian | tri+indv | intent 0.02 | 26.7->22.4 | -4.3 | [-5.6, -3.2] | [-8.6, -1.2] | 2.0/2.0 |
| Persian | tri+gate | intent 0.01 | 17.6->28.3 | +10.7 | [9.7, 11.9] | [0.7, 20.5] | 0.9/1.4 |
| Persian | tri+gate | intent 0.02 | 26.7->46.2 | +19.4 | [17.9, 20.9] | [12.8, 27.1] | 2.0/2.8 |
| Persian | tri+gate+ind | intent 0.01 | 17.6->25.7 | +8.1 | [6.9, 9.4] | [1.6, 12.1] | 0.9/1.5 |
| Persian | tri+gate+ind | intent 0.02 | 26.7->32.3 | +5.6 | [4.3, 7.0] | [1.1, 9.6] | 2.0/2.5 |
| Persian | minilm+ind | intent 0.01 | 13.6->17.0 | +3.5 | [2.5, 4.4] | [-3.0, 6.2] | 1.1/1.2 |
| Persian | minilm+ind | intent 0.02 | 24.2->23.8 | -0.4 | [-1.6, 0.8] | [-4.4, 4.1] | 2.3/2.5 |
| Persian | minilm+freq | intent 0.01 | 13.6->16.4 | +2.8 | [1.8, 3.8] | [-3.0, 5.4] | 1.1/1.4 |
| Persian | minilm+freq | intent 0.02 | 24.2->21.1 | -3.1 | [-4.1, -2.0] | [-6.1, 1.2] | 2.3/2.0 |
| Persian | minilm+dep | intent 0.01 | 13.6->12.8 | -0.8 | [-1.1, -0.5] | [-1.7, 0.3] | 1.1/0.9 |
| Persian | minilm+dep | intent 0.02 | 24.2->22.7 | -1.5 | [-2.2, -0.9] | [-2.7, 1.5] | 2.3/2.3 |
| Persian | minilm+indv | intent 0.01 | 13.6->16.5 | +2.9 | [1.9, 3.9] | [-2.8, 6.6] | 1.1/1.0 |
| Persian | minilm+indv | intent 0.02 | 24.2->22.8 | -1.4 | [-2.7, 0.0] | [-4.9, 2.8] | 2.3/2.3 |
| Persian | minilm+gate | intent 0.01 | 13.6->23.7 | +10.1 | [8.9, 11.2] | [2.7, 17.7] | 1.1/1.3 |
| Persian | minilm+gate | intent 0.02 | 24.2->39.4 | +15.1 | [13.8, 16.4] | [8.7, 20.0] | 2.3/2.4 |
| Persian | minilm+gate+ind | intent 0.01 | 13.6->26.1 | +12.5 | [11.1, 14.0] | [4.8, 16.4] | 1.1/1.1 |
| Persian | minilm+gate+ind | intent 0.02 | 24.2->32.6 | +8.4 | [6.9, 9.9] | [4.1, 13.6] | 2.3/2.1 |
| Persian | minilm+pet_i | intent 0.01 | 13.6->16.3 | +2.7 | [1.5, 3.9] | [-3.4, 7.1] | 1.1/0.7 |
| Persian | minilm+pet_i | intent 0.02 | 24.2->24.3 | +0.1 | [-1.5, 1.6] | [-4.9, 4.8] | 2.3/1.6 |
| Persian | minilm+pet_s | intent 0.01 | 13.6->9.5 | -4.1 | [-5.1, -3.0] | [-10.5, -0.3] | 1.1/0.9 |
| Persian | minilm+pet_s | intent 0.02 | 24.2->13.9 | -10.3 | [-11.8, -8.8] | [-14.5, -4.5] | 2.3/2.0 |
| Persian | mpnet+ind | intent 0.01 | 13.7->18.4 | +4.8 | [3.7, 5.8] | [-0.5, 10.0] | 1.1/1.0 |
| Persian | mpnet+ind | intent 0.02 | 25.6->26.4 | +0.9 | [-0.5, 2.2] | [-4.6, 7.6] | 2.2/2.1 |
| Persian | mpnet+freq | intent 0.01 | 13.7->14.1 | +0.4 | [-0.4, 1.2] | [-4.0, 5.9] | 1.1/0.9 |
| Persian | mpnet+freq | intent 0.02 | 25.6->25.3 | -0.3 | [-1.5, 1.0] | [-6.7, 5.3] | 2.2/2.0 |
| Persian | mpnet+dep | intent 0.01 | 13.7->12.8 | -0.9 | [-1.3, -0.5] | [-1.3, 5.3] | 1.1/0.9 |
| Persian | mpnet+dep | intent 0.02 | 25.6->27.3 | +1.7 | [0.8, 2.6] | [-2.8, 5.9] | 2.2/2.1 |
| Persian | mpnet+indv | intent 0.01 | 13.7->17.4 | +3.8 | [2.7, 4.8] | [-1.0, 9.6] | 1.1/1.0 |
| Persian | mpnet+indv | intent 0.02 | 25.6->25.3 | -0.3 | [-1.8, 1.1] | [-5.7, 6.5] | 2.2/2.0 |
| Persian | mpnet+gate | intent 0.01 | 13.7->20.0 | +6.4 | [5.4, 7.3] | [1.3, 16.0] | 1.1/1.1 |
| Persian | mpnet+gate | intent 0.02 | 25.6->34.4 | +8.8 | [7.8, 10.0] | [3.4, 17.5] | 2.2/2.1 |
| Persian | mpnet+gate+ind | intent 0.01 | 13.7->28.5 | +14.8 | [13.3, 16.3] | [6.3, 21.1] | 1.1/1.3 |
| Persian | mpnet+gate+ind | intent 0.02 | 25.6->34.7 | +9.2 | [7.6, 10.7] | [3.1, 15.9] | 2.2/2.3 |
| Persian | mpnet+pet_i | intent 0.01 | 13.7->23.1 | +9.4 | [8.1, 10.8] | [1.9, 16.6] | 1.1/1.2 |
| Persian | mpnet+pet_i | intent 0.02 | 25.6->29.9 | +4.4 | [2.8, 6.0] | [-1.4, 12.2] | 2.2/2.0 |
| Persian | mpnet+pet_s | intent 0.01 | 13.7->13.5 | -0.1 | [-1.3, 1.0] | [-5.4, 5.5] | 1.1/1.2 |
| Persian | mpnet+pet_s | intent 0.02 | 25.6->17.6 | -7.9 | [-9.4, -6.4] | [-14.1, -0.1] | 2.2/2.0 |
| Persian | e5+ind | intent 0.01 | 14.6->16.0 | +1.4 | [0.6, 2.3] | [-3.4, 6.6] | 0.9/0.8 |
| Persian | e5+ind | intent 0.02 | 26.8->24.4 | -2.4 | [-3.6, -1.3] | [-7.7, 2.9] | 2.1/1.9 |
| Persian | e5+freq | intent 0.01 | 14.6->16.3 | +1.7 | [0.9, 2.6] | [-3.1, 6.5] | 0.9/0.8 |
| Persian | e5+freq | intent 0.02 | 26.8->25.7 | -1.2 | [-2.3, -0.1] | [-6.3, 3.7] | 2.1/2.2 |
| Persian | e5+dep | intent 0.01 | 14.6->14.0 | -0.6 | [-0.9, -0.3] | [-1.4, 1.2] | 0.9/0.8 |
| Persian | e5+dep | intent 0.02 | 26.8->27.1 | +0.3 | [-0.5, 1.0] | [-2.8, 3.5] | 2.1/2.3 |
| Persian | e5+indv | intent 0.01 | 14.6->15.3 | +0.8 | [-0.1, 1.6] | [-2.7, 6.8] | 0.9/0.8 |
| Persian | e5+indv | intent 0.02 | 26.8->24.1 | -2.7 | [-4.1, -1.5] | [-7.5, 3.5] | 2.1/1.9 |
| Persian | e5+gate | intent 0.01 | 14.6->26.7 | +12.1 | [10.9, 13.3] | [2.8, 23.2] | 0.9/1.0 |
| Persian | e5+gate | intent 0.02 | 26.8->43.9 | +17.1 | [15.5, 18.5] | [10.6, 23.2] | 2.1/2.6 |
| Persian | e5+gate+ind | intent 0.01 | 14.6->27.4 | +12.9 | [11.5, 14.3] | [5.9, 16.5] | 0.9/1.2 |
| Persian | e5+gate+ind | intent 0.02 | 26.8->32.0 | +5.2 | [3.7, 6.6] | [-0.6, 12.7] | 2.1/1.8 |
| Persian | e5+pet_i | intent 0.01 | 14.6->23.2 | +8.7 | [7.3, 10.1] | [2.9, 13.9] | 0.9/1.0 |
| Persian | e5+pet_i | intent 0.02 | 26.8->31.7 | +4.9 | [3.3, 6.5] | [-0.9, 11.9] | 2.1/1.6 |
| Persian | e5+pet_s | intent 0.01 | 14.6->12.9 | -1.6 | [-2.8, -0.5] | [-6.4, 3.9] | 0.9/0.7 |
| Persian | e5+pet_s | intent 0.02 | 26.8->21.3 | -5.6 | [-7.1, -4.1] | [-11.6, 0.6] | 2.1/1.6 |
| Persian | bgem3+ind | intent 0.01 | 18.1->21.3 | +3.2 | [2.1, 4.2] | [-3.6, 7.6] | 0.9/1.1 |
| Persian | bgem3+ind | intent 0.02 | 31.6->26.7 | -4.9 | [-6.2, -3.7] | [-10.8, 1.7] | 2.0/2.0 |
| Persian | bgem3+freq | intent 0.01 | 18.1->17.6 | -0.4 | [-1.2, 0.3] | [-4.0, 6.8] | 0.9/0.9 |
| Persian | bgem3+freq | intent 0.02 | 31.6->30.5 | -1.1 | [-2.4, -0.0] | [-6.5, 4.8] | 2.0/2.5 |
| Persian | bgem3+dep | intent 0.01 | 18.1->18.9 | +0.9 | [0.3, 1.4] | [-2.0, 2.8] | 0.9/0.9 |
| Persian | bgem3+dep | intent 0.02 | 31.6->31.2 | -0.5 | [-1.3, 0.3] | [-3.6, 3.9] | 2.0/1.9 |
| Persian | bgem3+indv | intent 0.01 | 18.1->22.0 | +3.9 | [2.7, 5.0] | [-3.7, 8.0] | 0.9/1.1 |
| Persian | bgem3+indv | intent 0.02 | 31.6->27.4 | -4.2 | [-5.6, -2.8] | [-11.1, 1.6] | 2.0/2.2 |
| Persian | bgem3+gate | intent 0.01 | 18.1->26.7 | +8.6 | [7.6, 9.6] | [0.4, 19.4] | 0.9/0.8 |
| Persian | bgem3+gate | intent 0.02 | 31.6->48.4 | +16.7 | [15.3, 18.1] | [8.8, 23.2] | 2.0/2.2 |
| Persian | bgem3+gate+ind | intent 0.01 | 18.1->30.3 | +12.2 | [10.8, 13.7] | [2.9, 16.5] | 0.9/1.4 |
| Persian | bgem3+gate+ind | intent 0.02 | 31.6->36.7 | +5.0 | [3.4, 6.6] | [-2.1, 10.8] | 2.0/2.3 |
| Persian | bgem3+pet_i | intent 0.01 | 18.1->19.2 | +1.1 | [-0.3, 2.6] | [-6.6, 7.4] | 0.9/0.7 |
| Persian | bgem3+pet_i | intent 0.02 | 31.6->31.0 | -0.7 | [-2.3, 1.1] | [-9.0, 6.7] | 2.0/1.3 |
| Persian | bgem3+pet_s | intent 0.01 | 18.1->13.3 | -4.7 | [-6.0, -3.4] | [-11.7, 0.8] | 0.9/0.8 |
| Persian | bgem3+pet_s | intent 0.02 | 31.6->23.7 | -8.0 | [-9.6, -6.3] | [-15.4, -1.0] | 2.0/2.1 |
| Persian | minilmft | intent 0.01 | 13.6->13.7 | +0.1 | [-0.7, 0.9] | [-5.4, 2.8] | 1.1/0.8 |
| Persian | minilmft | intent 0.02 | 24.2->26.7 | +2.4 | [1.2, 3.7] | [-4.2, 7.3] | 2.3/2.7 |
| Persian | minilmft+ind | intent 0.01 | 13.7->14.4 | +0.7 | [0.1, 1.4] | [-1.9, 8.6] | 0.8/0.9 |
| Persian | minilmft+ind | intent 0.02 | 26.7->24.5 | -2.1 | [-3.0, -1.2] | [-5.5, 5.2] | 2.7/2.5 |
| Persian | minilmft+freq | intent 0.01 | 13.7->14.2 | +0.5 | [-0.2, 1.1] | [-2.8, 6.1] | 0.8/0.9 |
| Persian | minilmft+freq | intent 0.02 | 26.7->23.8 | -2.8 | [-3.7, -1.9] | [-6.7, 3.4] | 2.7/2.4 |
| Persian | minilmft+dep | intent 0.01 | 13.7->13.1 | -0.6 | [-0.9, -0.3] | [-1.3, -0.2] | 0.8/0.7 |
| Persian | minilmft+dep | intent 0.02 | 26.7->27.6 | +0.9 | [0.2, 1.6] | [-4.6, 1.2] | 2.7/2.8 |
| Persian | minilmft+indv | intent 0.01 | 13.7->16.0 | +2.4 | [1.5, 3.2] | [-1.7, 10.2] | 0.8/1.2 |
| Persian | minilmft+indv | intent 0.02 | 26.7->25.1 | -1.6 | [-2.7, -0.5] | [-5.6, 5.6] | 2.7/2.6 |
| Persian | minilmft+pet_i | intent 0.01 | 13.7->13.3 | -0.4 | [-1.6, 1.0] | [-4.9, 7.4] | 0.8/0.9 |
| Persian | minilmft+pet_i | intent 0.02 | 26.7->20.5 | -6.2 | [-7.8, -4.3] | [-11.7, 2.0] | 2.7/1.7 |
| Persian | minilmft+pet_s | intent 0.01 | 13.7->11.1 | -2.6 | [-3.7, -1.4] | [-8.7, 2.7] | 0.8/1.5 |
| Persian | minilmft+pet_s | intent 0.02 | 26.7->15.2 | -11.5 | [-12.9, -9.8] | [-16.9, -3.3] | 2.7/2.4 |
| Persian | ce | intent 0.01 | 18.1->22.4 | +4.3 | [3.3, 5.4] | [-2.4, 8.0] | 0.9/1.0 |
| Persian | ce | intent 0.02 | 31.6->29.5 | -2.2 | [-3.5, -1.0] | [-7.8, 2.5] | 2.0/2.0 |
| Persian | ce+ind | intent 0.01 | 22.4->21.0 | -1.4 | [-2.5, -0.4] | [-4.7, 3.4] | 1.0/1.2 |
| Persian | ce+ind | intent 0.02 | 29.5->26.7 | -2.8 | [-4.1, -1.3] | [-6.6, 0.9] | 2.0/2.2 |
| Persian | tri+ind | strict 0.02 | 10.0->11.5 | +1.5 | [1.0, 2.0] | [0.4, 3.9] | 2.4/2.1 |
| Persian | tri+ind | strict 0.05 | 14.0->20.8 | +6.8 | [5.7, 7.8] | [4.8, 9.1] | 5.4/5.4 |
| Persian | tri+freq | strict 0.02 | 10.0->10.5 | +0.5 | [0.1, 0.9] | [-0.4, 1.5] | 2.4/2.5 |
| Persian | tri+freq | strict 0.05 | 14.0->15.0 | +1.0 | [0.4, 1.6] | [-0.3, 2.1] | 5.4/5.4 |
| Persian | tri+dep | strict 0.02 | 10.0->10.7 | +0.7 | [0.4, 1.1] | [-0.1, 1.7] | 2.4/2.9 |
| Persian | tri+dep | strict 0.05 | 14.0->14.3 | +0.2 | [-0.0, 0.5] | [-0.1, 1.3] | 5.4/5.3 |
| Persian | tri+indv | strict 0.02 | 10.0->12.0 | +2.0 | [1.4, 2.6] | [0.4, 4.0] | 2.4/2.0 |
| Persian | tri+indv | strict 0.05 | 14.0->19.9 | +5.9 | [4.8, 6.9] | [4.1, 7.6] | 5.4/5.5 |
| Persian | tri+gate | strict 0.02 | 10.0->10.1 | +0.1 | [-0.1, 0.2] | [-0.1, 0.9] | 2.4/2.6 |
| Persian | tri+gate | strict 0.05 | 14.0->14.3 | +0.2 | [0.0, 0.5] | [-0.1, 1.0] | 5.4/5.5 |
| Persian | tri+gate+ind | strict 0.02 | 10.0->13.2 | +3.2 | [2.5, 3.9] | [0.6, 5.9] | 2.4/2.3 |
| Persian | tri+gate+ind | strict 0.05 | 14.0->24.7 | +10.7 | [9.5, 12.0] | [7.8, 12.5] | 5.4/6.4 |
| Persian | minilm+ind | strict 0.02 | 8.9->11.6 | +2.7 | [2.0, 3.4] | [0.4, 5.6] | 2.4/2.5 |
| Persian | minilm+ind | strict 0.05 | 13.1->21.5 | +8.3 | [7.2, 9.4] | [5.5, 10.8] | 5.3/6.1 |
| Persian | minilm+freq | strict 0.02 | 8.9->9.2 | +0.3 | [-0.1, 0.8] | [-0.6, 1.6] | 2.4/2.2 |
| Persian | minilm+freq | strict 0.05 | 13.1->15.2 | +2.1 | [1.2, 2.9] | [-0.0, 3.1] | 5.3/5.4 |
| Persian | minilm+dep | strict 0.02 | 8.9->8.7 | -0.1 | [-0.5, 0.2] | [-0.9, 0.3] | 2.4/2.4 |
| Persian | minilm+dep | strict 0.05 | 13.1->13.0 | -0.1 | [-0.5, 0.3] | [-0.9, 1.3] | 5.3/5.0 |
| Persian | minilm+indv | strict 0.02 | 8.9->11.4 | +2.5 | [1.8, 3.2] | [0.6, 5.8] | 2.4/2.4 |
| Persian | minilm+indv | strict 0.05 | 13.1->20.9 | +7.8 | [6.7, 9.0] | [5.4, 9.9] | 5.3/5.7 |
| Persian | minilm+gate | strict 0.02 | 8.9->9.3 | +0.4 | [0.1, 0.7] | [-0.2, 1.4] | 2.4/2.4 |
| Persian | minilm+gate | strict 0.05 | 13.1->15.1 | +2.0 | [1.5, 2.5] | [0.1, 3.1] | 5.3/6.0 |
| Persian | minilm+gate+ind | strict 0.02 | 8.9->14.1 | +5.2 | [4.3, 6.1] | [1.4, 7.5] | 2.4/2.6 |
| Persian | minilm+gate+ind | strict 0.05 | 13.1->25.1 | +12.0 | [10.6, 13.2] | [9.0, 13.7] | 5.3/6.1 |
| Persian | minilm+pet_i | strict 0.02 | 8.9->6.6 | -2.3 | [-3.0, -1.5] | [-3.7, -0.9] | 2.4/2.7 |
| Persian | minilm+pet_i | strict 0.05 | 13.1->9.5 | -3.6 | [-4.6, -2.6] | [-6.2, -2.3] | 5.3/5.3 |
| Persian | minilm+pet_s | strict 0.02 | 8.9->7.7 | -1.1 | [-1.9, -0.3] | [-2.7, 0.1] | 2.4/2.5 |
| Persian | minilm+pet_s | strict 0.05 | 13.1->10.7 | -2.5 | [-3.5, -1.4] | [-4.9, -0.8] | 5.3/5.2 |
| Persian | mpnet+ind | strict 0.02 | 8.6->12.6 | +4.0 | [3.2, 4.7] | [2.4, 7.0] | 2.3/2.3 |
| Persian | mpnet+ind | strict 0.05 | 14.4->22.5 | +8.1 | [6.9, 9.3] | [4.9, 11.0] | 5.4/5.4 |
| Persian | mpnet+freq | strict 0.02 | 8.6->9.5 | +0.9 | [0.4, 1.4] | [-0.7, 2.1] | 2.3/1.9 |
| Persian | mpnet+freq | strict 0.05 | 14.4->15.2 | +0.7 | [-0.1, 1.6] | [-0.4, 3.3] | 5.4/4.5 |
| Persian | mpnet+dep | strict 0.02 | 8.6->8.8 | +0.2 | [-0.1, 0.5] | [-0.4, 1.0] | 2.3/2.3 |
| Persian | mpnet+dep | strict 0.05 | 14.4->15.3 | +0.9 | [0.3, 1.4] | [-0.5, 2.0] | 5.4/5.3 |
| Persian | mpnet+indv | strict 0.02 | 8.6->13.6 | +5.0 | [4.1, 5.8] | [2.6, 7.0] | 2.3/2.4 |
| Persian | mpnet+indv | strict 0.05 | 14.4->23.1 | +8.7 | [7.4, 9.9] | [6.1, 10.9] | 5.4/5.7 |
| Persian | mpnet+gate | strict 0.02 | 8.6->9.0 | +0.3 | [0.1, 0.6] | [-0.1, 2.5] | 2.3/2.3 |
| Persian | mpnet+gate | strict 0.05 | 14.4->15.5 | +1.1 | [0.6, 1.5] | [-0.1, 2.2] | 5.4/5.6 |
| Persian | mpnet+gate+ind | strict 0.02 | 8.6->15.2 | +6.6 | [5.6, 7.5] | [3.8, 9.2] | 2.3/2.6 |
| Persian | mpnet+gate+ind | strict 0.05 | 14.4->26.2 | +11.7 | [10.4, 13.0] | [8.9, 14.5] | 5.4/6.0 |
| Persian | mpnet+pet_i | strict 0.02 | 8.6->6.8 | -1.8 | [-2.5, -1.1] | [-3.6, -0.6] | 2.3/2.9 |
| Persian | mpnet+pet_i | strict 0.05 | 14.4->9.4 | -5.0 | [-6.1, -3.9] | [-6.9, -2.9] | 5.4/5.5 |
| Persian | mpnet+pet_s | strict 0.02 | 8.6->8.0 | -0.7 | [-1.5, 0.1] | [-2.4, 0.9] | 2.3/2.3 |
| Persian | mpnet+pet_s | strict 0.05 | 14.4->12.1 | -2.4 | [-3.4, -1.2] | [-4.3, -0.2] | 5.4/5.3 |
| Persian | e5+ind | strict 0.02 | 9.4->9.9 | +0.5 | [0.1, 0.9] | [-0.4, 4.3] | 2.3/1.8 |
| Persian | e5+ind | strict 0.05 | 13.7->21.9 | +8.3 | [7.2, 9.4] | [5.7, 10.2] | 4.5/5.5 |
| Persian | e5+freq | strict 0.02 | 9.4->9.4 | +0.0 | [-0.4, 0.5] | [-1.3, 1.2] | 2.3/2.2 |
| Persian | e5+freq | strict 0.05 | 13.7->15.4 | +1.7 | [1.0, 2.5] | [0.0, 3.7] | 4.5/5.1 |
| Persian | e5+dep | strict 0.02 | 9.4->9.2 | -0.2 | [-0.4, -0.1] | [-0.4, 1.2] | 2.3/2.2 |
| Persian | e5+dep | strict 0.05 | 13.7->14.7 | +1.1 | [0.5, 1.6] | [-0.7, 2.0] | 4.5/4.5 |
| Persian | e5+indv | strict 0.02 | 9.4->10.8 | +1.4 | [0.9, 2.0] | [-0.4, 4.9] | 2.3/1.9 |
| Persian | e5+indv | strict 0.05 | 13.7->21.7 | +8.0 | [6.9, 9.1] | [5.8, 10.0] | 4.5/5.2 |
| Persian | e5+gate | strict 0.02 | 9.4->9.3 | -0.1 | [-0.2, 0.0] | [-0.3, 1.3] | 2.3/2.1 |
| Persian | e5+gate | strict 0.05 | 13.7->15.1 | +1.5 | [1.0, 2.0] | [-0.3, 2.0] | 4.5/4.9 |
| Persian | e5+gate+ind | strict 0.02 | 9.4->12.5 | +3.2 | [2.4, 3.9] | [0.3, 8.3] | 2.3/2.1 |
| Persian | e5+gate+ind | strict 0.05 | 13.7->25.1 | +11.5 | [10.2, 12.7] | [8.8, 13.4] | 4.5/5.7 |
| Persian | e5+pet_i | strict 0.02 | 9.4->6.7 | -2.7 | [-3.5, -2.0] | [-4.1, -1.0] | 2.3/2.4 |
| Persian | e5+pet_i | strict 0.05 | 13.7->10.4 | -3.3 | [-4.2, -2.3] | [-6.0, -2.0] | 4.5/6.6 |
| Persian | e5+pet_s | strict 0.02 | 9.4->8.1 | -1.2 | [-2.1, -0.5] | [-2.8, 0.6] | 2.3/2.4 |
| Persian | e5+pet_s | strict 0.05 | 13.7->13.1 | -0.5 | [-1.5, 0.5] | [-2.7, 1.8] | 4.5/5.2 |
| Persian | bgem3+ind | strict 0.02 | 10.9->12.9 | +2.1 | [1.4, 2.7] | [0.6, 5.1] | 2.7/2.3 |
| Persian | bgem3+ind | strict 0.05 | 15.2->24.6 | +9.4 | [8.2, 10.6] | [7.2, 11.5] | 4.5/5.8 |
| Persian | bgem3+freq | strict 0.02 | 10.9->11.2 | +0.3 | [-0.2, 0.8] | [-0.7, 1.8] | 2.7/2.4 |
| Persian | bgem3+freq | strict 0.05 | 15.2->17.2 | +2.0 | [1.2, 2.8] | [-0.3, 3.4] | 4.5/5.0 |
| Persian | bgem3+dep | strict 0.02 | 10.9->10.4 | -0.5 | [-0.8, -0.3] | [-0.8, 0.6] | 2.7/2.4 |
| Persian | bgem3+dep | strict 0.05 | 15.2->16.7 | +1.5 | [0.9, 2.1] | [-0.0, 2.7] | 4.5/4.6 |
| Persian | bgem3+indv | strict 0.02 | 10.9->12.6 | +1.7 | [1.1, 2.4] | [0.4, 5.8] | 2.7/2.2 |
| Persian | bgem3+indv | strict 0.05 | 15.2->24.0 | +8.8 | [7.6, 10.0] | [6.8, 10.7] | 4.5/6.1 |
| Persian | bgem3+gate | strict 0.02 | 10.9->10.8 | -0.1 | [-0.2, 0.0] | [-0.2, 1.1] | 2.7/2.4 |
| Persian | bgem3+gate | strict 0.05 | 15.2->16.2 | +1.1 | [0.7, 1.5] | [-0.2, 1.6] | 4.5/4.5 |
| Persian | bgem3+gate+ind | strict 0.02 | 10.9->13.7 | +2.8 | [2.1, 3.6] | [1.0, 7.9] | 2.7/2.3 |
| Persian | bgem3+gate+ind | strict 0.05 | 15.2->26.8 | +11.6 | [10.4, 13.0] | [9.6, 13.7] | 4.5/6.1 |
| Persian | bgem3+pet_i | strict 0.02 | 10.9->6.7 | -4.2 | [-5.1, -3.4] | [-5.6, -2.4] | 2.7/2.8 |
| Persian | bgem3+pet_i | strict 0.05 | 15.2->9.4 | -5.7 | [-6.8, -4.6] | [-7.8, -3.6] | 4.5/5.2 |
| Persian | bgem3+pet_s | strict 0.02 | 10.9->8.1 | -2.8 | [-3.8, -1.9] | [-4.1, -0.4] | 2.7/2.1 |
| Persian | bgem3+pet_s | strict 0.05 | 15.2->13.1 | -2.1 | [-3.3, -1.0] | [-4.3, -0.2] | 4.5/5.2 |
| Persian | minilmft | strict 0.02 | 8.9->9.8 | +0.9 | [0.3, 1.4] | [-1.3, 2.9] | 2.4/1.9 |
| Persian | minilmft | strict 0.05 | 13.1->18.3 | +5.2 | [4.2, 6.1] | [2.3, 7.8] | 5.3/5.4 |
| Persian | minilmft+ind | strict 0.02 | 9.8->12.8 | +3.0 | [2.3, 3.7] | [-0.0, 5.4] | 1.9/2.5 |
| Persian | minilmft+ind | strict 0.05 | 18.3->23.3 | +5.0 | [4.0, 6.1] | [1.7, 7.7] | 5.4/6.2 |
| Persian | minilmft+freq | strict 0.02 | 9.8->10.9 | +1.1 | [0.6, 1.6] | [-0.9, 4.0] | 1.9/2.0 |
| Persian | minilmft+freq | strict 0.05 | 18.3->20.6 | +2.4 | [1.4, 3.3] | [-0.3, 5.0] | 5.4/5.5 |
| Persian | minilmft+dep | strict 0.02 | 9.8->9.3 | -0.4 | [-0.7, -0.2] | [-2.5, 1.6] | 1.9/1.8 |
| Persian | minilmft+dep | strict 0.05 | 18.3->17.2 | -1.1 | [-1.5, -0.7] | [-1.6, 1.5] | 5.4/5.0 |
| Persian | minilmft+indv | strict 0.02 | 9.8->12.5 | +2.8 | [2.1, 3.5] | [0.3, 7.6] | 1.9/2.5 |
| Persian | minilmft+indv | strict 0.05 | 18.3->23.4 | +5.1 | [4.0, 6.2] | [2.3, 8.6] | 5.4/6.0 |
| Persian | minilmft+pet_i | strict 0.02 | 9.8->7.1 | -2.7 | [-3.5, -1.8] | [-5.3, -0.2] | 1.9/2.7 |
| Persian | minilmft+pet_i | strict 0.05 | 18.3->10.7 | -7.6 | [-8.8, -6.2] | [-11.2, -4.3] | 5.4/6.1 |
| Persian | minilmft+pet_s | strict 0.02 | 9.8->7.6 | -2.2 | [-3.0, -1.3] | [-4.8, 0.2] | 1.9/2.4 |
| Persian | minilmft+pet_s | strict 0.05 | 18.3->10.7 | -7.6 | [-8.9, -6.3] | [-10.8, -4.0] | 5.4/5.5 |
| Persian | ce | strict 0.02 | 10.9->11.1 | +0.2 | [-0.5, 1.0] | [-1.1, 1.8] | 2.7/2.6 |
| Persian | ce | strict 0.05 | 15.2->17.5 | +2.4 | [1.5, 3.2] | [0.6, 4.1] | 4.5/5.0 |
| Persian | ce+ind | strict 0.02 | 11.1->14.6 | +3.5 | [2.7, 4.3] | [0.6, 5.6] | 2.6/2.3 |
| Persian | ce+ind | strict 0.05 | 17.5->23.3 | +5.8 | [4.7, 7.0] | [3.3, 7.8] | 5.0/6.3 |
| English | tri+ind | intent 0.01 | 22.0->22.6 | +0.6 | [-0.5, 1.7] | [-3.9, 3.6] | 0.9/1.6 |
| English | tri+ind | intent 0.02 | 33.0->27.4 | -5.6 | [-6.8, -4.3] | [-9.1, 1.7] | 2.5/2.6 |
| English | tri+freq | intent 0.01 | 22.0->21.0 | -1.0 | [-1.8, -0.2] | [-4.7, 2.0] | 0.9/1.1 |
| English | tri+freq | intent 0.02 | 33.0->27.2 | -5.8 | [-6.8, -4.8] | [-8.5, 0.6] | 2.5/2.2 |
| English | tri+indv | intent 0.01 | 22.0->21.9 | -0.1 | [-1.3, 1.0] | [-4.4, 3.0] | 0.9/1.7 |
| English | tri+indv | intent 0.02 | 33.0->25.7 | -7.3 | [-8.6, -5.9] | [-10.9, 0.1] | 2.5/2.8 |
| English | tri+gate | intent 0.01 | 22.0->38.7 | +16.7 | [15.4, 18.1] | [10.6, 23.0] | 0.9/1.2 |
| English | tri+gate | intent 0.02 | 33.0->48.2 | +15.2 | [13.9, 16.6] | [11.0, 25.4] | 2.5/2.2 |
| English | tri+gate+ind | intent 0.01 | 22.0->29.4 | +7.4 | [6.0, 8.7] | [2.5, 13.5] | 0.9/1.0 |
| English | tri+gate+ind | intent 0.02 | 33.0->36.9 | +3.9 | [2.2, 5.5] | [-0.3, 11.5] | 2.5/1.9 |
| English | minilm+ind | intent 0.01 | 24.0->23.7 | -0.3 | [-1.4, 0.7] | [-4.9, 5.6] | 0.8/1.0 |
| English | minilm+ind | intent 0.02 | 35.7->30.4 | -5.3 | [-6.6, -4.1] | [-9.6, 0.8] | 1.8/1.8 |
| English | minilm+freq | intent 0.01 | 24.0->21.5 | -2.5 | [-3.3, -1.7] | [-4.8, 3.6] | 0.8/0.7 |
| English | minilm+freq | intent 0.02 | 35.7->31.2 | -4.5 | [-5.6, -3.5] | [-8.8, -0.0] | 1.8/1.9 |
| English | minilm+indv | intent 0.01 | 24.0->22.6 | -1.4 | [-2.5, -0.4] | [-5.4, 5.1] | 0.8/0.8 |
| English | minilm+indv | intent 0.02 | 35.7->30.1 | -5.6 | [-7.0, -4.1] | [-10.5, -0.3] | 1.8/2.1 |
| English | minilm+gate | intent 0.01 | 24.0->37.4 | +13.4 | [12.0, 14.6] | [4.6, 21.5] | 0.8/1.1 |
| English | minilm+gate | intent 0.02 | 35.7->46.2 | +10.5 | [9.4, 11.7] | [5.1, 16.9] | 1.8/1.7 |
| English | minilm+gate+ind | intent 0.01 | 24.0->33.2 | +9.2 | [7.7, 10.6] | [2.6, 16.2] | 0.8/1.0 |
| English | minilm+gate+ind | intent 0.02 | 35.7->39.6 | +3.9 | [2.3, 5.5] | [-1.9, 10.4] | 1.8/2.0 |
| English | minilm+pet_i | intent 0.01 | 24.0->23.1 | -0.9 | [-2.6, 0.6] | [-8.2, 9.5] | 0.8/0.9 |
| English | minilm+pet_i | intent 0.02 | 35.7->36.7 | +1.0 | [-0.7, 2.6] | [-5.1, 7.3] | 1.8/2.0 |
| English | minilm+pet_s | intent 0.01 | 24.0->16.4 | -7.6 | [-9.2, -5.9] | [-14.8, -0.8] | 0.8/1.5 |
| English | minilm+pet_s | intent 0.02 | 35.7->22.8 | -12.9 | [-14.6, -11.0] | [-18.8, -6.1] | 1.8/2.3 |
| English | mpnet+ind | intent 0.01 | 24.8->21.5 | -3.3 | [-4.2, -2.4] | [-6.1, 4.6] | 1.1/0.8 |
| English | mpnet+ind | intent 0.02 | 32.4->28.8 | -3.6 | [-4.8, -2.4] | [-7.2, -0.2] | 1.6/1.8 |
| English | mpnet+freq | intent 0.01 | 24.8->22.3 | -2.5 | [-3.3, -1.6] | [-5.1, 5.1] | 1.1/0.8 |
| English | mpnet+freq | intent 0.02 | 32.4->30.7 | -1.7 | [-2.8, -0.5] | [-5.4, 1.9] | 1.6/2.0 |
| English | mpnet+indv | intent 0.01 | 24.8->21.6 | -3.2 | [-4.2, -2.2] | [-6.6, 4.2] | 1.1/0.8 |
| English | mpnet+indv | intent 0.02 | 32.4->28.2 | -4.2 | [-5.6, -2.8] | [-8.6, -1.4] | 1.6/2.1 |
| English | mpnet+gate | intent 0.01 | 24.8->32.4 | +7.6 | [6.6, 8.6] | [3.5, 17.2] | 1.1/0.8 |
| English | mpnet+gate | intent 0.02 | 32.4->46.4 | +14.0 | [12.8, 15.3] | [7.0, 18.5] | 1.6/1.5 |
| English | mpnet+gate+ind | intent 0.01 | 24.8->31.5 | +6.7 | [5.3, 8.2] | [0.3, 15.9] | 1.1/0.9 |
| English | mpnet+gate+ind | intent 0.02 | 32.4->39.0 | +6.6 | [4.9, 8.2] | [1.4, 10.5] | 1.6/1.8 |
| English | mpnet+pet_i | intent 0.01 | 24.8->23.8 | -1.0 | [-2.7, 0.8] | [-6.8, 8.9] | 1.1/0.9 |
| English | mpnet+pet_i | intent 0.02 | 32.4->36.3 | +3.9 | [2.2, 5.8] | [-3.5, 9.4] | 1.6/2.0 |
| English | mpnet+pet_s | intent 0.01 | 24.8->13.3 | -11.4 | [-13.1, -9.7] | [-17.8, -2.7] | 1.1/1.1 |
| English | mpnet+pet_s | intent 0.02 | 32.4->20.8 | -11.6 | [-13.4, -9.7] | [-17.0, -6.5] | 1.6/1.9 |
| English | e5+ind | intent 0.01 | 21.8->22.5 | +0.7 | [-0.4, 1.8] | [-4.8, 6.4] | 0.9/1.1 |
| English | e5+ind | intent 0.02 | 32.4->29.2 | -3.3 | [-4.6, -2.0] | [-7.4, 0.5] | 1.7/2.1 |
| English | e5+freq | intent 0.01 | 21.8->22.3 | +0.6 | [-0.4, 1.5] | [-4.4, 5.1] | 0.9/1.1 |
| English | e5+freq | intent 0.02 | 32.4->28.3 | -4.1 | [-5.2, -3.0] | [-7.3, 0.5] | 1.7/1.6 |
| English | e5+indv | intent 0.01 | 21.8->21.9 | +0.1 | [-1.1, 1.3] | [-5.8, 5.0] | 0.9/1.1 |
| English | e5+indv | intent 0.02 | 32.4->27.5 | -4.9 | [-6.4, -3.6] | [-8.7, -0.7] | 1.7/2.2 |
| English | e5+gate | intent 0.01 | 21.8->34.6 | +12.8 | [11.6, 14.1] | [4.1, 19.2] | 0.9/0.8 |
| English | e5+gate | intent 0.02 | 32.4->46.4 | +14.0 | [12.6, 15.3] | [8.0, 22.9] | 1.7/1.3 |
| English | e5+gate+ind | intent 0.01 | 21.8->34.3 | +12.5 | [11.0, 14.2] | [3.9, 18.2] | 0.9/1.0 |
| English | e5+gate+ind | intent 0.02 | 32.4->40.1 | +7.6 | [5.9, 9.3] | [2.9, 12.9] | 1.7/1.8 |
| English | e5+pet_i | intent 0.01 | 21.8->27.5 | +5.7 | [4.1, 7.3] | [-1.2, 12.3] | 0.9/0.9 |
| English | e5+pet_i | intent 0.02 | 32.4->36.9 | +4.4 | [2.9, 6.1] | [-2.8, 9.6] | 1.7/1.8 |
| English | e5+pet_s | intent 0.01 | 21.8->15.4 | -6.3 | [-7.9, -4.7] | [-13.5, 1.4] | 0.9/0.7 |
| English | e5+pet_s | intent 0.02 | 32.4->24.3 | -8.1 | [-9.8, -6.5] | [-13.8, -1.4] | 1.7/1.6 |
| English | bgem3+ind | intent 0.01 | 24.0->23.9 | -0.0 | [-1.1, 1.0] | [-4.2, 4.2] | 0.8/1.0 |
| English | bgem3+ind | intent 0.02 | 36.9->30.1 | -6.9 | [-8.0, -5.6] | [-10.5, 0.3] | 2.2/1.7 |
| English | bgem3+freq | intent 0.01 | 24.0->21.5 | -2.5 | [-3.3, -1.6] | [-5.9, 0.1] | 0.8/0.7 |
| English | bgem3+freq | intent 0.02 | 36.9->30.9 | -6.0 | [-7.0, -5.0] | [-9.1, -0.4] | 2.2/1.5 |
| English | bgem3+indv | intent 0.01 | 24.0->21.9 | -2.1 | [-3.2, -0.9] | [-6.0, 3.1] | 0.8/0.9 |
| English | bgem3+indv | intent 0.02 | 36.9->29.3 | -7.6 | [-9.0, -6.1] | [-12.2, -1.3] | 2.2/2.0 |
| English | bgem3+gate | intent 0.01 | 24.0->36.9 | +12.9 | [11.8, 14.2] | [3.0, 19.3] | 0.8/1.0 |
| English | bgem3+gate | intent 0.02 | 36.9->50.5 | +13.6 | [12.3, 14.9] | [7.1, 20.8] | 2.2/1.7 |
| English | bgem3+gate+ind | intent 0.01 | 24.0->33.7 | +9.8 | [8.3, 11.2] | [2.9, 14.9] | 0.8/1.0 |
| English | bgem3+gate+ind | intent 0.02 | 36.9->41.4 | +4.5 | [2.9, 6.2] | [-0.9, 11.6] | 2.2/1.9 |
| English | bgem3+pet_i | intent 0.01 | 24.0->27.8 | +3.8 | [2.1, 5.5] | [-4.1, 11.5] | 0.8/1.0 |
| English | bgem3+pet_i | intent 0.02 | 36.9->41.2 | +4.2 | [2.5, 5.9] | [-3.0, 11.3] | 2.2/1.8 |
| English | bgem3+pet_s | intent 0.01 | 24.0->19.3 | -4.6 | [-6.3, -2.9] | [-12.0, 0.8] | 0.8/1.2 |
| English | bgem3+pet_s | intent 0.02 | 36.9->29.3 | -7.6 | [-9.3, -5.9] | [-13.5, 1.6] | 2.2/1.9 |
| English | minilmft | intent 0.01 | 24.0->22.7 | -1.3 | [-2.5, -0.3] | [-5.9, 5.9] | 0.8/0.8 |
| English | minilmft | intent 0.02 | 35.7->30.2 | -5.5 | [-6.8, -4.3] | [-11.1, -0.4] | 1.8/1.8 |
| English | minilmft+ind | intent 0.01 | 22.7->22.3 | -0.3 | [-1.1, 0.4] | [-3.0, 4.5] | 0.8/0.7 |
| English | minilmft+ind | intent 0.02 | 30.2->29.8 | -0.4 | [-1.4, 0.6] | [-3.2, 3.9] | 1.8/2.1 |
| English | minilmft+freq | intent 0.01 | 22.7->19.8 | -2.9 | [-3.5, -2.3] | [-4.9, 0.2] | 0.8/0.7 |
| English | minilmft+freq | intent 0.02 | 30.2->25.2 | -5.0 | [-5.8, -4.2] | [-6.4, -0.8] | 1.8/1.3 |
| English | minilmft+indv | intent 0.01 | 22.7->23.4 | +0.8 | [-0.1, 1.7] | [-3.3, 4.8] | 0.8/1.1 |
| English | minilmft+indv | intent 0.02 | 30.2->29.4 | -0.8 | [-1.9, 0.3] | [-3.1, 4.3] | 1.8/2.0 |
| English | minilmft+pet_i | intent 0.01 | 22.7->10.5 | -12.2 | [-13.8, -10.5] | [-16.9, -7.5] | 0.8/0.8 |
| English | minilmft+pet_i | intent 0.02 | 30.2->17.4 | -12.8 | [-14.6, -10.8] | [-17.7, -6.2] | 1.8/1.4 |
| English | minilmft+pet_s | intent 0.01 | 22.7->7.5 | -15.1 | [-16.7, -13.5] | [-20.3, -11.2] | 0.8/0.9 |
| English | minilmft+pet_s | intent 0.02 | 30.2->11.2 | -18.9 | [-20.6, -17.0] | [-23.2, -13.3] | 1.8/1.7 |
| English | ce | intent 0.01 | 24.0->21.4 | -2.6 | [-3.8, -1.3] | [-8.3, 1.7] | 0.8/0.9 |
| English | ce | intent 0.02 | 36.9->34.0 | -2.9 | [-4.3, -1.6] | [-8.7, 3.3] | 2.2/1.8 |
| English | ce+ind | intent 0.01 | 21.4->23.0 | +1.6 | [0.3, 2.8] | [-3.5, 7.2] | 0.9/1.1 |
| English | ce+ind | intent 0.02 | 34.0->29.5 | -4.5 | [-5.9, -3.1] | [-10.5, 2.2] | 1.8/2.0 |
| English | tri+ind | strict 0.02 | 12.9->16.4 | +3.5 | [2.8, 4.3] | [1.5, 5.6] | 2.6/2.4 |
| English | tri+ind | strict 0.05 | 15.1->23.9 | +8.9 | [7.7, 10.0] | [6.8, 10.5] | 4.9/5.6 |
| English | tri+freq | strict 0.02 | 12.9->13.3 | +0.5 | [0.1, 0.8] | [-0.3, 1.4] | 2.6/2.1 |
| English | tri+freq | strict 0.05 | 15.1->16.4 | +1.3 | [0.8, 1.8] | [0.3, 2.3] | 4.9/4.6 |
| English | tri+indv | strict 0.02 | 12.9->15.9 | +3.0 | [2.3, 3.8] | [1.3, 5.8] | 2.6/2.2 |
| English | tri+indv | strict 0.05 | 15.1->23.0 | +7.9 | [6.8, 9.0] | [6.1, 9.3] | 4.9/5.6 |
| English | tri+gate | strict 0.02 | 12.9->12.9 | +0.0 | [0.0, 0.0] | [0.0, 0.6] | 2.6/2.6 |
| English | tri+gate | strict 0.05 | 15.1->15.5 | +0.5 | [0.2, 0.7] | [0.0, 0.9] | 4.9/4.7 |
| English | tri+gate+ind | strict 0.02 | 12.9->19.2 | +6.4 | [5.4, 7.3] | [2.4, 8.6] | 2.6/2.5 |
| English | tri+gate+ind | strict 0.05 | 15.1->26.8 | +11.7 | [10.5, 12.9] | [9.2, 13.8] | 4.9/5.5 |
| English | minilm+ind | strict 0.02 | 9.5->15.8 | +6.3 | [5.4, 7.3] | [2.6, 11.2] | 2.4/2.2 |
| English | minilm+ind | strict 0.05 | 17.6->26.9 | +9.3 | [8.1, 10.5] | [7.4, 12.3] | 5.3/4.9 |
| English | minilm+freq | strict 0.02 | 9.5->10.4 | +0.9 | [0.4, 1.5] | [-0.7, 3.2] | 2.4/2.3 |
| English | minilm+freq | strict 0.05 | 17.6->19.0 | +1.4 | [0.7, 2.3] | [-0.2, 3.3] | 5.3/5.2 |
| English | minilm+indv | strict 0.02 | 9.5->16.4 | +6.9 | [5.9, 7.9] | [2.9, 11.0] | 2.4/2.2 |
| English | minilm+indv | strict 0.05 | 17.6->26.8 | +9.2 | [7.9, 10.4] | [6.7, 11.7] | 5.3/4.9 |
| English | minilm+gate | strict 0.02 | 9.5->10.6 | +1.1 | [0.6, 1.5] | [-0.3, 2.1] | 2.4/2.7 |
| English | minilm+gate | strict 0.05 | 17.6->17.8 | +0.2 | [-0.2, 0.6] | [-0.4, 2.1] | 5.3/5.2 |
| English | minilm+gate+ind | strict 0.02 | 9.5->19.8 | +10.3 | [9.1, 11.5] | [5.7, 14.4] | 2.4/2.6 |
| English | minilm+gate+ind | strict 0.05 | 17.6->29.5 | +11.9 | [10.6, 13.2] | [9.9, 15.7] | 5.3/5.0 |
| English | minilm+pet_i | strict 0.02 | 9.5->4.3 | -5.2 | [-6.3, -4.2] | [-7.7, -1.7] | 2.4/2.5 |
| English | minilm+pet_i | strict 0.05 | 17.6->9.0 | -8.6 | [-9.9, -7.3] | [-10.6, -5.9] | 5.3/4.8 |
| English | minilm+pet_s | strict 0.02 | 9.5->7.5 | -2.1 | [-3.3, -0.9] | [-5.9, 1.6] | 2.4/1.9 |
| English | minilm+pet_s | strict 0.05 | 17.6->13.0 | -4.6 | [-6.0, -3.3] | [-6.9, -1.8] | 5.3/4.9 |
| English | mpnet+ind | strict 0.02 | 9.5->16.7 | +7.2 | [6.2, 8.2] | [3.2, 10.3] | 2.3/2.6 |
| English | mpnet+ind | strict 0.05 | 16.4->27.4 | +11.0 | [9.8, 12.2] | [7.9, 13.5] | 5.2/5.4 |
| English | mpnet+freq | strict 0.02 | 9.5->10.1 | +0.6 | [0.1, 1.2] | [-0.9, 2.4] | 2.3/2.2 |
| English | mpnet+freq | strict 0.05 | 16.4->17.7 | +1.3 | [0.5, 2.1] | [-0.3, 3.2] | 5.2/4.6 |
| English | mpnet+indv | strict 0.02 | 9.5->16.2 | +6.8 | [5.7, 7.8] | [3.0, 10.1] | 2.3/2.4 |
| English | mpnet+indv | strict 0.05 | 16.4->25.8 | +9.3 | [8.1, 10.5] | [7.0, 12.3] | 5.2/4.8 |
| English | mpnet+gate | strict 0.02 | 9.5->10.0 | +0.5 | [0.3, 0.8] | [-0.1, 1.7] | 2.3/2.6 |
| English | mpnet+gate | strict 0.05 | 16.4->17.3 | +0.9 | [0.5, 1.3] | [-0.2, 2.1] | 5.2/5.4 |
| English | mpnet+gate+ind | strict 0.02 | 9.5->19.7 | +10.3 | [9.1, 11.4] | [4.8, 13.4] | 2.3/2.5 |
| English | mpnet+gate+ind | strict 0.05 | 16.4->31.1 | +14.6 | [13.2, 16.1] | [12.0, 17.1] | 5.2/5.1 |
| English | mpnet+pet_i | strict 0.02 | 9.5->4.1 | -5.3 | [-6.5, -4.2] | [-7.6, -3.0] | 2.3/1.8 |
| English | mpnet+pet_i | strict 0.05 | 16.4->9.4 | -7.1 | [-8.4, -5.8] | [-9.6, -4.6] | 5.2/5.2 |
| English | mpnet+pet_s | strict 0.02 | 9.5->7.0 | -2.5 | [-3.7, -1.3] | [-5.0, 0.3] | 2.3/2.2 |
| English | mpnet+pet_s | strict 0.05 | 16.4->12.6 | -3.8 | [-5.2, -2.4] | [-6.7, -0.7] | 5.2/5.2 |
| English | e5+ind | strict 0.02 | 9.0->16.9 | +7.9 | [6.9, 9.0] | [2.9, 11.8] | 2.2/2.5 |
| English | e5+ind | strict 0.05 | 14.7->27.1 | +12.4 | [11.1, 13.7] | [9.4, 14.1] | 4.3/5.1 |
| English | e5+freq | strict 0.02 | 9.0->10.6 | +1.6 | [1.0, 2.3] | [-0.8, 2.9] | 2.2/2.1 |
| English | e5+freq | strict 0.05 | 14.7->16.9 | +2.2 | [1.4, 3.0] | [0.1, 4.2] | 4.3/4.8 |
| English | e5+indv | strict 0.02 | 9.0->16.0 | +7.0 | [6.0, 8.1] | [2.8, 10.7] | 2.2/2.3 |
| English | e5+indv | strict 0.05 | 14.7->26.0 | +11.3 | [10.0, 12.7] | [8.2, 13.5] | 4.3/4.8 |
| English | e5+gate | strict 0.02 | 9.0->8.9 | -0.1 | [-0.2, 0.0] | [-0.2, 1.6] | 2.2/2.0 |
| English | e5+gate | strict 0.05 | 14.7->15.6 | +1.0 | [0.6, 1.4] | [-0.3, 2.6] | 4.3/4.4 |
| English | e5+gate+ind | strict 0.02 | 9.0->19.3 | +10.3 | [9.1, 11.5] | [5.1, 14.1] | 2.2/2.2 |
| English | e5+gate+ind | strict 0.05 | 14.7->31.3 | +16.6 | [15.2, 18.1] | [13.1, 18.8] | 4.3/4.9 |
| English | e5+pet_i | strict 0.02 | 9.0->5.4 | -3.6 | [-4.6, -2.5] | [-6.2, -2.1] | 2.2/2.7 |
| English | e5+pet_i | strict 0.05 | 14.7->10.0 | -4.7 | [-6.0, -3.4] | [-7.0, -2.1] | 4.3/5.3 |
| English | e5+pet_s | strict 0.02 | 9.0->8.3 | -0.7 | [-1.9, 0.4] | [-3.6, 1.0] | 2.2/2.4 |
| English | e5+pet_s | strict 0.05 | 14.7->13.2 | -1.4 | [-2.7, -0.2] | [-3.8, 1.0] | 4.3/4.6 |
| English | bgem3+ind | strict 0.02 | 10.8->19.3 | +8.5 | [7.4, 9.7] | [4.6, 11.6] | 2.3/2.1 |
| English | bgem3+ind | strict 0.05 | 17.9->28.1 | +10.3 | [9.0, 11.5] | [8.0, 13.3] | 5.0/4.7 |
| English | bgem3+freq | strict 0.02 | 10.8->12.0 | +1.2 | [0.6, 1.9] | [-0.7, 3.5] | 2.3/2.4 |
| English | bgem3+freq | strict 0.05 | 17.9->18.6 | +0.7 | [-0.1, 1.5] | [-1.1, 2.2] | 5.0/4.7 |
| English | bgem3+indv | strict 0.02 | 10.8->18.1 | +7.3 | [6.2, 8.4] | [4.1, 10.4] | 2.3/1.9 |
| English | bgem3+indv | strict 0.05 | 17.9->27.1 | +9.2 | [7.9, 10.5] | [6.9, 11.4] | 5.0/4.7 |
| English | bgem3+gate | strict 0.02 | 10.8->10.8 | +0.0 | [-0.1, 0.2] | [-0.1, 1.1] | 2.3/2.1 |
| English | bgem3+gate | strict 0.05 | 17.9->18.6 | +0.7 | [0.4, 1.0] | [0.0, 1.6] | 5.0/5.0 |
| English | bgem3+gate+ind | strict 0.02 | 10.8->20.9 | +10.1 | [8.9, 11.4] | [7.2, 14.1] | 2.3/2.1 |
| English | bgem3+gate+ind | strict 0.05 | 17.9->32.1 | +14.2 | [12.8, 15.6] | [11.5, 16.2] | 5.0/4.7 |
| English | bgem3+pet_i | strict 0.02 | 10.8->4.3 | -6.4 | [-7.5, -5.3] | [-8.7, -3.1] | 2.3/2.5 |
| English | bgem3+pet_i | strict 0.05 | 17.9->10.2 | -7.7 | [-9.0, -6.4] | [-10.2, -5.6] | 5.0/5.7 |
| English | bgem3+pet_s | strict 0.02 | 10.8->8.0 | -2.8 | [-4.0, -1.6] | [-5.6, 0.7] | 2.3/2.5 |
| English | bgem3+pet_s | strict 0.05 | 17.9->12.9 | -5.0 | [-6.4, -3.6] | [-7.3, -2.6] | 5.0/4.9 |
| English | minilmft | strict 0.02 | 9.5->18.0 | +8.5 | [7.4, 9.5] | [4.3, 11.2] | 2.4/2.6 |
| English | minilmft | strict 0.05 | 17.6->24.5 | +6.9 | [5.7, 8.0] | [4.3, 10.6] | 5.3/4.7 |
| English | minilmft+ind | strict 0.02 | 18.0->18.5 | +0.5 | [-0.2, 1.1] | [-1.4, 4.5] | 2.6/2.3 |
| English | minilmft+ind | strict 0.05 | 24.5->29.5 | +5.0 | [3.8, 6.1] | [1.9, 7.5] | 4.7/5.4 |
| English | minilmft+freq | strict 0.02 | 18.0->16.3 | -1.7 | [-2.2, -1.2] | [-2.4, 2.5] | 2.6/2.1 |
| English | minilmft+freq | strict 0.05 | 24.5->25.3 | +0.8 | [-0.2, 1.8] | [-2.3, 2.6] | 4.7/4.7 |
| English | minilmft+indv | strict 0.02 | 18.0->18.3 | +0.3 | [-0.4, 0.9] | [-1.6, 5.0] | 2.6/2.2 |
| English | minilmft+indv | strict 0.05 | 24.5->29.5 | +5.0 | [3.8, 6.2] | [1.9, 7.5] | 4.7/5.4 |
| English | minilmft+pet_i | strict 0.02 | 18.0->4.5 | -13.5 | [-14.8, -12.1] | [-15.8, -7.4] | 2.6/1.9 |
| English | minilmft+pet_i | strict 0.05 | 24.5->9.2 | -15.3 | [-16.8, -13.6] | [-19.1, -12.3] | 4.7/5.1 |
| English | minilmft+pet_s | strict 0.02 | 18.0->4.4 | -13.6 | [-14.9, -12.1] | [-16.0, -7.4] | 2.6/1.5 |
| English | minilmft+pet_s | strict 0.05 | 24.5->8.6 | -15.8 | [-17.3, -14.2] | [-19.6, -12.7] | 4.7/4.3 |
| English | ce | strict 0.02 | 10.8->9.5 | -1.2 | [-2.1, -0.4] | [-2.8, 1.9] | 2.3/1.8 |
| English | ce | strict 0.05 | 17.9->17.7 | -0.2 | [-1.2, 0.8] | [-2.2, 1.5] | 5.0/5.8 |
| English | ce+ind | strict 0.02 | 9.5->15.5 | +6.0 | [5.0, 6.9] | [2.4, 9.5] | 1.8/2.2 |
| English | ce+ind | strict 0.05 | 17.7->26.8 | +9.1 | [7.9, 10.4] | [6.0, 11.7] | 5.8/4.7 |

- Budget excess on test, unguarded (+ind comparisons, 40 cells): 25 exceed; median excess among those 0.29 points; median over all cells 0.13; max 0.66
- Budget excess on test, guarded (+ind comparisons, 40 cells): 26 exceed; median excess among those 0.38 points; median over all cells 0.11; max 1.12
- Budget excess on test, candidates +ind (40 cells): 26 exceed; max 1.12 points; plain max 0.66
- Budget excess on test, candidates +gate (40 cells): 26 exceed; max 1.02 points; plain max 0.66
- Budget excess on test, candidates +gate+ind (40 cells): 31 exceed; max 1.42 points; plain max 0.66

## Equal test error: best safe-hit rate on the test curve within each budget

### Persian, intent

| method | U<=0.01 | U<=0.02 |
|---|---|---|
| bgem3 | 20.2 | 32.4 |
| bgem3+dep | 18.9 | 31.2 |
| bgem3+freq | 18.5 | 27.0 |
| bgem3+gate | 32.5 | 46.3 |
| bgem3+gate+ind | 27.3 | 35.3 |
| bgem3+ind | 20.0 | 26.7 |
| bgem3+indv | 19.5 | 26.8 |
| bgem3+pet_i | 26.7 | 38.1 |
| bgem3+pet_s | 15.2 | 23.0 |
| ce | 20.4 | 30.0 |
| ce+ind | 18.6 | 25.9 |
| e5 | 17.2 | 24.2 |
| e5+dep | 18.3 | 24.9 |
| e5+freq | 17.8 | 24.3 |
| e5+gate | 26.7 | 34.5 |
| e5+gate+ind | 23.0 | 32.7 |
| e5+ind | 17.4 | 24.4 |
| e5+indv | 17.8 | 24.1 |
| e5+pet_i | 23.2 | 34.5 |
| e5+pet_s | 15.8 | 23.6 |
| minilm | 12.6 | 21.4 |
| minilm+dep | 14.1 | 20.7 |
| minilm+freq | 13.3 | 20.6 |
| minilm+gate | 20.2 | 34.2 |
| minilm+gate+ind | 21.3 | 31.9 |
| minilm+ind | 14.5 | 20.7 |
| minilm+indv | 16.2 | 21.3 |
| minilm+pet_i | 18.6 | 26.7 |
| minilm+pet_s | 9.8 | 13.9 |
| minilmft | 13.7 | 21.9 |
| minilmft+dep | 13.1 | 20.4 |
| minilmft+freq | 14.2 | 21.5 |
| minilmft+ind | 14.4 | 20.5 |
| minilmft+indv | 14.1 | 21.3 |
| minilmft+pet_i | 16.3 | 21.1 |
| minilmft+pet_s | 9.7 | 13.0 |
| mpnet | 11.8 | 21.5 |
| mpnet+dep | 13.2 | 25.6 |
| mpnet+freq | 14.6 | 25.3 |
| mpnet+gate | 17.7 | 33.4 |
| mpnet+gate+ind | 22.7 | 32.5 |
| mpnet+ind | 16.2 | 25.6 |
| mpnet+indv | 17.4 | 25.1 |
| mpnet+pet_i | 18.0 | 29.3 |
| mpnet+pet_s | 10.5 | 17.6 |
| tri | 18.5 | 26.5 |
| tri+dep | 20.0 | 26.9 |
| tri+freq | 17.8 | 24.7 |
| tri+gate | 23.0 | 36.3 |
| tri+gate+ind | 22.1 | 30.0 |
| tri+ind | 17.6 | 23.6 |
| tri+indv | 17.0 | 22.3 |

### Persian, strict

| method | U<=0.02 | U<=0.05 |
|---|---|---|
| bgem3 | 8.3 | 16.3 |
| bgem3+dep | 8.5 | 17.5 |
| bgem3+freq | 9.5 | 16.8 |
| bgem3+gate | 8.8 | 17.4 |
| bgem3+gate+ind | 12.6 | 25.2 |
| bgem3+ind | 10.9 | 22.6 |
| bgem3+indv | 11.2 | 22.9 |
| bgem3+pet_i | 6.3 | 9.1 |
| bgem3+pet_s | 8.0 | 12.7 |
| ce | 9.4 | 17.2 |
| ce+ind | 12.3 | 20.9 |
| e5 | 8.3 | 13.7 |
| e5+dep | 8.1 | 14.7 |
| e5+freq | 8.5 | 14.4 |
| e5+gate | 8.2 | 15.1 |
| e5+gate+ind | 11.0 | 23.7 |
| e5+ind | 11.1 | 19.9 |
| e5+indv | 10.8 | 21.1 |
| e5+pet_i | 6.3 | 8.6 |
| e5+pet_s | 7.4 | 12.2 |
| minilm | 8.0 | 12.4 |
| minilm+dep | 7.7 | 12.5 |
| minilm+freq | 9.0 | 14.2 |
| minilm+gate | 8.3 | 13.1 |
| minilm+gate+ind | 10.7 | 22.4 |
| minilm+ind | 9.5 | 18.7 |
| minilm+indv | 9.7 | 19.6 |
| minilm+pet_i | 6.3 | 8.9 |
| minilm+pet_s | 7.1 | 10.3 |
| minilmft | 9.8 | 16.1 |
| minilmft+dep | 9.3 | 17.2 |
| minilmft+freq | 10.9 | 18.7 |
| minilmft+ind | 9.2 | 19.7 |
| minilmft+indv | 9.2 | 20.7 |
| minilmft+pet_i | 6.5 | 9.7 |
| minilmft+pet_s | 7.1 | 10.2 |
| mpnet | 7.7 | 13.2 |
| mpnet+dep | 7.9 | 14.4 |
| mpnet+freq | 10.1 | 15.7 |
| mpnet+gate | 8.1 | 14.3 |
| mpnet+gate+ind | 11.2 | 23.4 |
| mpnet+ind | 10.8 | 21.3 |
| mpnet+indv | 10.6 | 21.9 |
| mpnet+pet_i | 5.9 | 9.0 |
| mpnet+pet_s | 7.7 | 11.9 |
| tri | 9.0 | 13.3 |
| tri+dep | 8.9 | 14.0 |
| tri+freq | 9.4 | 14.5 |
| tri+gate | 9.0 | 13.7 |
| tri+gate+ind | 12.1 | 21.2 |
| tri+ind | 11.3 | 20.2 |
| tri+indv | 11.4 | 18.9 |

### English, intent

| method | U<=0.01 | U<=0.02 |
|---|---|---|
| bgem3 | 25.9 | 34.5 |
| bgem3+freq | 25.2 | 34.2 |
| bgem3+gate | 37.9 | 52.8 |
| bgem3+gate+ind | 33.1 | 41.5 |
| bgem3+ind | 23.9 | 31.1 |
| bgem3+indv | 22.4 | 29.3 |
| bgem3+pet_i | 28.3 | 42.6 |
| bgem3+pet_s | 16.8 | 29.3 |
| ce | 22.0 | 35.3 |
| ce+ind | 20.0 | 29.5 |
| e5 | 21.8 | 34.6 |
| e5+freq | 19.6 | 30.0 |
| e5+gate | 39.0 | 53.7 |
| e5+gate+ind | 33.2 | 40.8 |
| e5+ind | 19.7 | 28.0 |
| e5+indv | 19.8 | 26.3 |
| e5+pet_i | 27.5 | 36.9 |
| e5+pet_s | 18.8 | 26.4 |
| minilm | 26.4 | 37.0 |
| minilm+freq | 25.2 | 31.9 |
| minilm+gate | 35.9 | 49.9 |
| minilm+gate+ind | 32.6 | 39.4 |
| minilm+ind | 24.2 | 30.8 |
| minilm+indv | 23.4 | 29.8 |
| minilm+pet_i | 24.7 | 37.5 |
| minilm+pet_s | 12.6 | 19.8 |
| minilmft | 22.7 | 30.2 |
| minilmft+freq | 21.6 | 28.1 |
| minilmft+ind | 22.3 | 29.0 |
| minilmft+indv | 21.8 | 29.4 |
| minilmft+pet_i | 11.5 | 20.6 |
| minilmft+pet_s | 7.5 | 12.7 |
| mpnet | 22.4 | 37.1 |
| mpnet+freq | 23.7 | 30.7 |
| mpnet+gate | 39.4 | 50.7 |
| mpnet+gate+ind | 32.6 | 40.2 |
| mpnet+ind | 22.8 | 29.3 |
| mpnet+indv | 22.3 | 27.7 |
| mpnet+pet_i | 24.9 | 35.9 |
| mpnet+pet_s | 12.0 | 21.4 |
| tri | 22.7 | 29.3 |
| tri+freq | 20.4 | 25.9 |
| tri+gate | 35.1 | 46.9 |
| tri+gate+ind | 28.7 | 36.9 |
| tri+ind | 19.4 | 24.4 |
| tri+indv | 18.8 | 23.4 |

### English, strict

| method | U<=0.02 | U<=0.05 |
|---|---|---|
| bgem3 | 8.2 | 17.4 |
| bgem3+freq | 10.6 | 18.6 |
| bgem3+gate | 10.0 | 18.0 |
| bgem3+gate+ind | 19.9 | 32.6 |
| bgem3+ind | 18.1 | 28.4 |
| bgem3+indv | 18.1 | 28.2 |
| bgem3+pet_i | 3.9 | 8.4 |
| bgem3+pet_s | 6.6 | 12.9 |
| ce | 9.9 | 16.0 |
| ce+ind | 14.3 | 27.4 |
| e5 | 7.9 | 15.8 |
| e5+freq | 9.4 | 16.9 |
| e5+gate | 8.9 | 17.0 |
| e5+gate+ind | 17.9 | 31.3 |
| e5+ind | 14.4 | 26.4 |
| e5+indv | 13.9 | 26.0 |
| e5+pet_i | 4.3 | 9.3 |
| e5+pet_s | 6.9 | 13.2 |
| minilm | 8.1 | 15.7 |
| minilm+freq | 9.5 | 18.7 |
| minilm+gate | 7.9 | 17.2 |
| minilm+gate+ind | 16.6 | 29.5 |
| minilm+ind | 14.4 | 26.9 |
| minilm+indv | 14.3 | 26.8 |
| minilm+pet_i | 4.0 | 9.2 |
| minilm+pet_s | 7.8 | 13.0 |
| minilmft | 15.3 | 24.5 |
| minilmft+freq | 14.0 | 25.3 |
| minilmft+ind | 14.2 | 28.9 |
| minilmft+indv | 16.4 | 28.8 |
| minilmft+pet_i | 4.5 | 8.8 |
| minilmft+pet_s | 5.1 | 9.7 |
| mpnet | 7.9 | 15.5 |
| mpnet+freq | 9.0 | 18.2 |
| mpnet+gate | 8.7 | 16.3 |
| mpnet+gate+ind | 15.2 | 30.4 |
| mpnet+ind | 13.5 | 25.7 |
| mpnet+indv | 13.6 | 26.0 |
| mpnet+pet_i | 4.2 | 8.8 |
| mpnet+pet_s | 6.6 | 12.3 |
| tri | 12.3 | 15.1 |
| tri+freq | 13.1 | 16.8 |
| tri+gate | 12.5 | 15.9 |
| tri+gate+ind | 17.6 | 25.1 |
| tri+ind | 15.1 | 22.3 |
| tri+indv | 15.6 | 22.2 |

## Minimal pairs (Section 6.3, Table 5)

### Persian

- pairs 956, counts {'different_argument': 425, 'different_intent': 357, 'same_meaning': 174}, lexicon 4113
- AUC tri: {'different_intent': 0.8084, 'different_argument': 0.5449}; medians {'different_argument': 0.5, 'different_intent': 0.3478, 'same_meaning': 0.5181}
- AUC minilm: {'different_intent': 0.8477, 'different_argument': 0.752}; medians {'different_argument': 0.7002999782562256, 'different_intent': 0.5997999906539917, 'same_meaning': 0.8622000217437744}
- AUC e5: {'different_intent': 0.8311, 'different_argument': 0.7848}; medians {'different_argument': 0.9229000210762024, 'different_intent': 0.9214000105857849, 'same_meaning': 0.9563000202178955}
- AUC mpnet: {'different_intent': 0.884, 'different_argument': 0.7742}; medians {'different_argument': 0.723800003528595, 'different_intent': 0.5740000009536743, 'same_meaning': 0.8930000066757202}
- AUC bgem3: {'different_intent': 0.8862, 'different_argument': 0.8589}; medians {'different_argument': 0.7554000020027161, 'different_intent': 0.7421000003814697, 'same_meaning': 0.902999997138977}
- block rate blocked_ind: {'different_argument': 0.92, 'different_intent': 0.6022, 'same_meaning': 0.2586}
- block rate blocked_freq: {'different_argument': 0.6541, 'different_intent': 0.3838, 'same_meaning': 0.3851}
- block rate blocked_dep: {'different_argument': 0.12, 'different_intent': 0.1765, 'same_meaning': 0.1782}
- threshold matched to the induced guard's same-meaning block rate, tri: {'tau': 0.4286, 'same_meaning': 0.2471, 'different_intent': 0.7591, 'different_argument': 0.2306}
- threshold matched to the induced guard's same-meaning block rate, minilm: {'tau': 0.7515, 'same_meaning': 0.2586, 'different_intent': 0.7787, 'different_argument': 0.6212}
- threshold matched to the induced guard's same-meaning block rate, e5: {'tau': 0.94, 'same_meaning': 0.2586, 'different_intent': 0.7311, 'different_argument': 0.6588}
- threshold matched to the induced guard's same-meaning block rate, mpnet: {'tau': 0.802, 'same_meaning': 0.2586, 'different_intent': 0.8655, 'different_argument': 0.6635}
- threshold matched to the induced guard's same-meaning block rate, bgem3: {'tau': 0.8308, 'same_meaning': 0.2586, 'different_intent': 0.8375, 'different_argument': 0.7929}

### English

- pairs 1661, counts {'different_intent': 762, 'different_argument': 578, 'same_meaning': 321}, lexicon 4122
- AUC tri: {'different_intent': 0.7311, 'different_argument': 0.5139}; medians {'different_argument': 0.4444, 'different_intent': 0.3, 'same_meaning': 0.4375}
- AUC minilm: {'different_intent': 0.9221, 'different_argument': 0.8266}; medians {'different_argument': 0.5722000002861023, 'different_intent': 0.48330000042915344, 'same_meaning': 0.8086000084877014}
- AUC e5: {'different_intent': 0.848, 'different_argument': 0.8023}; medians {'different_argument': 0.8720999956130981, 'different_intent': 0.8715999722480774, 'same_meaning': 0.9253000020980835}
- AUC mpnet: {'different_intent': 0.9322, 'different_argument': 0.8333}; medians {'different_argument': 0.5848000049591064, 'different_intent': 0.47540000081062317, 'same_meaning': 0.8289999961853027}
- AUC bgem3: {'different_intent': 0.8843, 'different_argument': 0.8177}; medians {'different_argument': 0.7378000020980835, 'different_intent': 0.7260000109672546, 'same_meaning': 0.8726000189781189}
- block rate blocked_ind: {'different_argument': 0.8633, 'different_intent': 0.6693, 'same_meaning': 0.2087}
- block rate blocked_freq: {'different_argument': 0.7145, 'different_intent': 0.5197, 'same_meaning': 0.4237}
- threshold matched to the induced guard's same-meaning block rate, tri: {'tau': 0.2924, 'same_meaning': 0.2087, 'different_intent': 0.4239, 'different_argument': 0.192}
- threshold matched to the induced guard's same-meaning block rate, minilm: {'tau': 0.68, 'same_meaning': 0.2087, 'different_intent': 0.8871, 'different_argument': 0.7093}
- threshold matched to the induced guard's same-meaning block rate, e5: {'tau': 0.8902, 'same_meaning': 0.2087, 'different_intent': 0.689, 'different_argument': 0.628}
- threshold matched to the induced guard's same-meaning block rate, mpnet: {'tau': 0.6928, 'same_meaning': 0.2087, 'different_intent': 0.8898, 'different_argument': 0.7007}
- threshold matched to the induced guard's same-meaning block rate, bgem3: {'tau': 0.7926, 'same_meaning': 0.2087, 'different_intent': 0.7769, 'different_argument': 0.6747}

## Lexicon evidence (Section 7)

- Persian: 5405 words ever differed between two neighbours; 4113 critical (meta lexicon 4113)
  - تقویم: distinguishing 668, benign 120, ratio 0.848, critical False
  - حذف: distinguishing 529, benign 89, ratio 0.856, critical False
  - اضافه: distinguishing 341, benign 49, ratio 0.874, critical False
  - روشن: distinguishing 299, benign 91, ratio 0.767, critical False
  - کم: distinguishing 248, benign 34, ratio 0.879, critical False
  - بیشتر: distinguishing 193, benign 37, ratio 0.839, critical False
  - خاموش: distinguishing 193, benign 21, ratio 0.902, critical True
  - زیاد: distinguishing 79, benign 16, ratio 0.832, critical False
  - کمتر: distinguishing 70, benign 12, ratio 0.854, critical False
  - سوکت: distinguishing 66, benign 7, ratio 0.904, critical True
  - افزایش: distinguishing 47, benign 7, ratio 0.870, critical False
  - دوشاخه: distinguishing 38, benign 1, ratio 0.974, critical True
  - تقویمم: distinguishing 36, benign 0, ratio 1.000, critical True
  - کاهش: distinguishing 23, benign 7, ratio 0.767, critical False
- English: 5213 words ever differed between two neighbours; 4122 critical (meta lexicon 4122)
  - on: distinguishing 3432, benign 564, ratio 0.859, critical False
  - set: distinguishing 886, benign 189, ratio 0.824, critical False
  - up: distinguishing 844, benign 163, ratio 0.838, critical False
  - need: distinguishing 626, benign 203, ratio 0.755, critical False
  - will: distinguishing 555, benign 88, ratio 0.863, critical False
  - want: distinguishing 522, benign 180, ratio 0.744, critical False
  - like: distinguishing 516, benign 160, ratio 0.763, critical False
  - add: distinguishing 504, benign 106, ratio 0.826, critical False
  - off: distinguishing 389, benign 57, ratio 0.872, critical False
  - remove: distinguishing 263, benign 63, ratio 0.807, critical False
  - delete: distinguishing 257, benign 75, ratio 0.774, critical False
  - not: distinguishing 211, benign 26, ratio 0.890, critical False
  - down: distinguishing 168, benign 36, ratio 0.824, critical False
  - reply: distinguishing 143, benign 15, ratio 0.905, critical True
  - mute: distinguishing 113, benign 10, ratio 0.919, critical True
  - cancel: distinguishing 111, benign 15, ratio 0.881, critical False
  - wake: distinguishing 75, benign 13, ratio 0.852, critical False
  - lower: distinguishing 62, benign 13, ratio 0.827, critical False
  - louder: distinguishing 32, benign 17, ratio 0.653, critical False
  - respond: distinguishing 31, benign 2, ratio 0.939, critical True
  - quiet: distinguishing 30, benign 2, ratio 0.938, critical True
  - silence: distinguishing 2, benign 7, ratio 0.222, critical False

## Ablation without rule-tier intents (Section 6.4)

- Persian: pool 6852, queries 1836, reusable 52.9%
  - intent tri @ 0.8: safe 7.6 unsafe 0.3; +ind safe 7.1 unsafe 0.3
  - intent minilm @ 0.8: safe 53.6 unsafe 8.8; +ind safe 29.2 unsafe 4.4
  - intent minilm @ 0.9: safe 29.2 unsafe 3.1; +ind safe 19.1 unsafe 1.9
  - intent bgem3 @ 0.8: safe 56.9 unsafe 6.4; +ind safe 31.8 unsafe 3.3
  - intent bgem3 @ 0.9: safe 27.5 unsafe 1.3; +ind safe 19.6 unsafe 0.9
  - strict tri @ 0.8: safe 6.6 unsafe 1.4; +ind safe 6.4 unsafe 1.0
  - strict minilm @ 0.8: safe 27.9 unsafe 34.4; +ind safe 23.4 unsafe 10.2
  - strict minilm @ 0.9: safe 18.5 unsafe 13.8; +ind safe 16.1 unsafe 4.8
  - strict bgem3 @ 0.8: safe 31.9 unsafe 31.4; +ind safe 26.0 unsafe 9.1
  - strict bgem3 @ 0.9: safe 20.1 unsafe 8.7; +ind safe 17.0 unsafe 3.5
- English: pool 6784, queries 1836, reusable 50.5%
  - intent tri @ 0.8: safe 9.5 unsafe 0.0; +ind safe 8.6 unsafe 0.0
  - intent minilm @ 0.8: safe 49.0 unsafe 3.4; +ind safe 29.9 unsafe 1.6
  - intent minilm @ 0.9: safe 25.4 unsafe 0.7; +ind safe 18.6 unsafe 0.3
  - intent bgem3 @ 0.8: safe 59.7 unsafe 5.3; +ind safe 34.0 unsafe 3.0
  - intent bgem3 @ 0.9: safe 28.3 unsafe 1.3; +ind safe 20.5 unsafe 0.6
  - strict tri @ 0.8: safe 8.7 unsafe 0.8; +ind safe 8.4 unsafe 0.2
  - strict minilm @ 0.8: safe 31.9 unsafe 20.6; +ind safe 26.5 unsafe 5.0
  - strict minilm @ 0.9: safe 19.4 unsafe 6.6; +ind safe 16.8 unsafe 2.1
  - strict bgem3 @ 0.8: safe 34.7 unsafe 30.3; +ind safe 29.5 unsafe 7.6
  - strict bgem3 @ 0.9: safe 21.4 unsafe 8.2; +ind safe 19.1 unsafe 2.0

## Dev-chosen thresholds (_norules): change in safe hits, test (Tables 3-4)

| Language | Candidate | budget | safe plain->cand | d_safe | CI (test bootstrap) | CI (nested) | test unsafe plain/cand |
|---|---|---|---|---|---|---|---|
| Persian | tri+ind | intent 0.01 | 18.9->17.5 | -1.4 | [-2.6, -0.2] | [-6.4, 3.5] | 0.9/0.8 |
| Persian | tri+ind | intent 0.02 | 31.3->23.9 | -7.4 | [-9.0, -5.8] | [-11.9, 0.5] | 2.8/2.1 |
| Persian | tri+freq | intent 0.01 | 18.9->18.1 | -0.8 | [-2.0, 0.4] | [-6.8, 2.7] | 0.9/0.8 |
| Persian | tri+freq | intent 0.02 | 31.3->23.6 | -7.6 | [-9.2, -6.2] | [-12.7, 0.0] | 2.8/2.0 |
| Persian | tri+dep | intent 0.01 | 18.9->18.4 | -0.5 | [-0.9, -0.1] | [-2.8, 4.6] | 0.9/0.8 |
| Persian | tri+dep | intent 0.02 | 31.3->29.5 | -1.8 | [-2.5, -1.1] | [-5.2, 3.3] | 2.8/2.6 |
| Persian | tri+indv | intent 0.01 | 18.9->17.6 | -1.3 | [-2.7, 0.2] | [-7.1, 3.3] | 0.9/0.9 |
| Persian | tri+indv | intent 0.02 | 31.3->21.6 | -9.7 | [-11.5, -8.0] | [-15.3, -0.7] | 2.8/2.2 |
| Persian | tri+gate | intent 0.01 | 18.9->35.7 | +16.8 | [15.1, 18.7] | [2.6, 28.9] | 0.9/1.5 |
| Persian | tri+gate | intent 0.02 | 31.3->49.8 | +18.6 | [16.7, 20.4] | [12.6, 25.7] | 2.8/2.4 |
| Persian | tri+gate+ind | intent 0.01 | 18.9->26.9 | +8.0 | [6.2, 9.6] | [0.4, 13.7] | 0.9/1.3 |
| Persian | tri+gate+ind | intent 0.02 | 31.3->30.7 | -0.5 | [-2.5, 1.2] | [-6.7, 8.4] | 2.8/1.7 |
| Persian | minilm+ind | intent 0.01 | 18.1->14.3 | -3.9 | [-5.1, -2.7] | [-6.4, 4.3] | 1.4/1.1 |
| Persian | minilm+ind | intent 0.02 | 26.6->23.1 | -3.5 | [-5.1, -1.9] | [-6.0, 1.7] | 2.6/2.4 |
| Persian | minilm+freq | intent 0.01 | 18.1->15.4 | -2.7 | [-4.1, -1.4] | [-7.0, 6.3] | 1.4/1.1 |
| Persian | minilm+freq | intent 0.02 | 26.6->20.0 | -6.5 | [-8.0, -5.0] | [-8.7, 0.7] | 2.6/1.9 |
| Persian | minilm+dep | intent 0.01 | 18.1->17.9 | -0.3 | [-1.0, 0.4] | [-2.1, 4.2] | 1.4/1.3 |
| Persian | minilm+dep | intent 0.02 | 26.6->24.5 | -2.1 | [-2.8, -1.4] | [-2.6, 2.7] | 2.6/2.2 |
| Persian | minilm+indv | intent 0.01 | 18.1->14.4 | -3.8 | [-5.0, -2.4] | [-7.3, 3.8] | 1.4/1.1 |
| Persian | minilm+indv | intent 0.02 | 26.6->20.7 | -5.9 | [-7.6, -4.1] | [-8.2, -0.3] | 2.6/2.0 |
| Persian | minilm+gate | intent 0.01 | 18.1->26.3 | +8.2 | [6.9, 9.6] | [1.4, 17.2] | 1.4/1.3 |
| Persian | minilm+gate | intent 0.02 | 26.6->36.7 | +10.1 | [8.7, 11.5] | [6.3, 17.6] | 2.6/1.6 |
| Persian | minilm+gate+ind | intent 0.01 | 18.1->22.7 | +4.6 | [3.0, 6.2] | [0.4, 14.0] | 1.4/0.9 |
| Persian | minilm+gate+ind | intent 0.02 | 26.6->31.8 | +5.2 | [3.2, 7.1] | [0.1, 10.9] | 2.6/1.5 |
| Persian | minilm+pet_i | intent 0.01 | 18.1->16.8 | -1.3 | [-3.1, 0.5] | [-7.1, 7.6] | 1.4/0.5 |
| Persian | minilm+pet_i | intent 0.02 | 26.6->22.3 | -4.2 | [-6.4, -2.1] | [-8.5, 2.9] | 2.6/1.4 |
| Persian | minilm+pet_s | intent 0.01 | 18.1->8.6 | -9.5 | [-11.2, -7.8] | [-15.1, -0.7] | 1.4/0.9 |
| Persian | minilm+pet_s | intent 0.02 | 26.6->12.6 | -14.0 | [-16.0, -11.9] | [-18.2, -7.4] | 2.6/1.9 |
| Persian | bgem3+ind | intent 0.01 | 21.0->19.2 | -1.8 | [-3.0, -0.5] | [-9.6, 5.2] | 0.6/0.9 |
| Persian | bgem3+ind | intent 0.02 | 33.7->23.9 | -9.7 | [-11.3, -8.2] | [-14.0, -2.0] | 1.9/1.3 |
| Persian | bgem3+freq | intent 0.01 | 21.0->20.2 | -0.8 | [-2.3, 0.7] | [-8.8, 6.1] | 0.6/1.0 |
| Persian | bgem3+freq | intent 0.02 | 33.7->26.7 | -7.0 | [-8.6, -5.2] | [-13.8, 0.8] | 1.9/1.9 |
| Persian | bgem3+dep | intent 0.01 | 21.0->20.3 | -0.7 | [-1.5, 0.1] | [-3.3, 5.6] | 0.6/0.8 |
| Persian | bgem3+dep | intent 0.02 | 33.7->32.0 | -1.6 | [-2.3, -0.9] | [-4.2, 4.8] | 1.9/1.6 |
| Persian | bgem3+indv | intent 0.01 | 21.0->19.8 | -1.3 | [-2.7, 0.2] | [-9.1, 5.2] | 0.6/0.9 |
| Persian | bgem3+indv | intent 0.02 | 33.7->25.3 | -8.3 | [-10.1, -6.4] | [-15.0, -0.9] | 1.9/1.7 |
| Persian | bgem3+gate | intent 0.01 | 21.0->32.7 | +11.7 | [10.2, 13.2] | [-0.5, 21.0] | 0.6/0.9 |
| Persian | bgem3+gate | intent 0.02 | 33.7->48.4 | +14.7 | [13.0, 16.5] | [7.5, 21.1] | 1.9/1.5 |
| Persian | bgem3+gate+ind | intent 0.01 | 21.0->26.9 | +5.9 | [4.2, 7.6] | [-1.7, 13.6] | 0.6/0.9 |
| Persian | bgem3+gate+ind | intent 0.02 | 33.7->34.7 | +1.0 | [-0.9, 3.0] | [-6.8, 8.8] | 1.9/1.8 |
| Persian | bgem3+pet_i | intent 0.01 | 21.0->21.0 | +0.0 | [-2.0, 2.2] | [-9.5, 8.8] | 0.6/0.5 |
| Persian | bgem3+pet_i | intent 0.02 | 33.7->30.6 | -3.1 | [-5.2, -0.9] | [-10.9, 6.0] | 1.9/1.2 |
| Persian | bgem3+pet_s | intent 0.01 | 21.0->12.3 | -8.8 | [-10.6, -7.0] | [-17.7, -1.1] | 0.6/0.7 |
| Persian | bgem3+pet_s | intent 0.02 | 33.7->22.3 | -11.3 | [-13.4, -9.2] | [-18.8, -1.3] | 1.9/2.1 |
| Persian | tri+ind | strict 0.02 | 8.5->11.4 | +2.9 | [2.1, 3.8] | [0.9, 5.7] | 2.7/2.0 |
| Persian | tri+ind | strict 0.05 | 11.1->19.8 | +8.8 | [7.4, 10.1] | [5.8, 11.2] | 5.1/6.2 |
| Persian | tri+freq | strict 0.02 | 8.5->8.6 | +0.1 | [-0.5, 0.7] | [-0.9, 1.2] | 2.7/2.2 |
| Persian | tri+freq | strict 0.05 | 11.1->11.9 | +0.8 | [-0.1, 1.7] | [-0.6, 2.7] | 5.1/4.6 |
| Persian | tri+dep | strict 0.02 | 8.5->8.4 | -0.1 | [-0.3, 0.2] | [-0.4, 0.7] | 2.7/2.6 |
| Persian | tri+dep | strict 0.05 | 11.1->10.9 | -0.1 | [-0.4, 0.2] | [-0.4, 1.2] | 5.1/4.7 |
| Persian | tri+indv | strict 0.02 | 8.5->10.9 | +2.5 | [1.7, 3.3] | [0.7, 5.0] | 2.7/1.9 |
| Persian | tri+indv | strict 0.05 | 11.1->17.9 | +6.9 | [5.6, 8.2] | [4.8, 8.5] | 5.1/5.6 |
| Persian | tri+gate | strict 0.02 | 8.5->8.5 | +0.0 | [-0.2, 0.2] | [-0.3, 0.3] | 2.7/2.6 |
| Persian | tri+gate | strict 0.05 | 11.1->11.1 | +0.0 | [-0.2, 0.2] | [-0.2, 1.4] | 5.1/4.8 |
| Persian | tri+gate+ind | strict 0.02 | 8.5->12.6 | +4.1 | [3.3, 5.2] | [1.5, 7.8] | 2.7/2.2 |
| Persian | tri+gate+ind | strict 0.05 | 11.1->22.0 | +10.9 | [9.3, 12.5] | [8.4, 13.1] | 5.1/6.2 |
| Persian | minilm+ind | strict 0.02 | 7.8->11.2 | +3.3 | [2.4, 4.2] | [0.1, 6.8] | 3.2/2.5 |
| Persian | minilm+ind | strict 0.05 | 13.2->20.0 | +6.8 | [5.4, 8.3] | [4.4, 9.5] | 6.4/7.1 |
| Persian | minilm+freq | strict 0.02 | 7.8->8.2 | +0.4 | [-0.4, 1.1] | [-1.4, 3.3] | 3.2/2.2 |
| Persian | minilm+freq | strict 0.05 | 13.2->13.5 | +0.3 | [-0.8, 1.5] | [-1.7, 2.2] | 6.4/5.9 |
| Persian | minilm+dep | strict 0.02 | 7.8->7.0 | -0.8 | [-1.3, -0.4] | [-1.4, -0.2] | 3.2/2.6 |
| Persian | minilm+dep | strict 0.05 | 13.2->12.4 | -0.8 | [-1.3, -0.4] | [-1.6, 0.4] | 6.4/5.6 |
| Persian | minilm+indv | strict 0.02 | 7.8->10.9 | +3.1 | [2.2, 4.1] | [0.1, 6.4] | 3.2/2.3 |
| Persian | minilm+indv | strict 0.05 | 13.2->18.9 | +5.7 | [4.3, 7.2] | [3.4, 8.0] | 6.4/5.8 |
| Persian | minilm+gate | strict 0.02 | 7.8->8.1 | +0.2 | [-0.1, 0.5] | [-0.2, 1.6] | 3.2/2.8 |
| Persian | minilm+gate | strict 0.05 | 13.2->13.7 | +0.5 | [0.1, 1.0] | [-0.3, 2.1] | 6.4/6.5 |
| Persian | minilm+gate+ind | strict 0.02 | 7.8->13.5 | +5.6 | [4.5, 6.8] | [1.3, 10.8] | 3.2/2.7 |
| Persian | minilm+gate+ind | strict 0.05 | 13.2->22.9 | +9.7 | [8.1, 11.3] | [6.5, 12.2] | 6.4/6.4 |
| Persian | minilm+pet_i | strict 0.02 | 7.8->5.5 | -2.3 | [-3.3, -1.4] | [-4.0, -0.2] | 3.2/2.8 |
| Persian | minilm+pet_i | strict 0.05 | 13.2->7.8 | -5.3 | [-6.7, -4.0] | [-7.2, -2.7] | 6.4/4.9 |
| Persian | minilm+pet_s | strict 0.02 | 7.8->6.1 | -1.7 | [-2.8, -0.7] | [-3.3, 0.5] | 3.2/2.2 |
| Persian | minilm+pet_s | strict 0.05 | 13.2->8.5 | -4.7 | [-6.0, -3.3] | [-6.8, -2.1] | 6.4/5.5 |
| Persian | bgem3+ind | strict 0.02 | 9.7->14.8 | +5.1 | [3.9, 6.3] | [1.1, 7.8] | 2.8/2.7 |
| Persian | bgem3+ind | strict 0.05 | 14.5->22.5 | +8.0 | [6.5, 9.5] | [4.9, 10.3] | 4.6/5.9 |
| Persian | bgem3+freq | strict 0.02 | 9.7->9.6 | -0.1 | [-0.8, 0.7] | [-1.5, 1.9] | 2.8/2.4 |
| Persian | bgem3+freq | strict 0.05 | 14.5->15.7 | +1.1 | [-0.1, 2.4] | [-1.7, 3.3] | 4.6/5.6 |
| Persian | bgem3+dep | strict 0.02 | 9.7->9.5 | -0.2 | [-0.6, 0.2] | [-1.0, 1.0] | 2.8/2.7 |
| Persian | bgem3+dep | strict 0.05 | 14.5->15.4 | +0.9 | [0.2, 1.5] | [-0.8, 2.4] | 4.6/4.6 |
| Persian | bgem3+indv | strict 0.02 | 9.7->14.1 | +4.4 | [3.2, 5.6] | [0.6, 7.7] | 2.8/2.3 |
| Persian | bgem3+indv | strict 0.05 | 14.5->21.2 | +6.6 | [5.2, 8.2] | [4.0, 9.3] | 4.6/5.7 |
| Persian | bgem3+gate | strict 0.02 | 9.7->9.6 | -0.1 | [-0.3, 0.0] | [-0.3, 0.9] | 2.8/2.7 |
| Persian | bgem3+gate | strict 0.05 | 14.5->14.9 | +0.3 | [-0.1, 0.7] | [-0.3, 1.4] | 4.6/4.6 |
| Persian | bgem3+gate+ind | strict 0.02 | 9.7->14.8 | +5.1 | [4.0, 6.3] | [1.1, 9.9] | 2.8/2.5 |
| Persian | bgem3+gate+ind | strict 0.05 | 14.5->23.7 | +9.2 | [7.6, 10.7] | [6.6, 12.6] | 4.6/5.8 |
| Persian | bgem3+pet_i | strict 0.02 | 9.7->5.3 | -4.4 | [-5.5, -3.3] | [-6.4, -2.8] | 2.8/3.0 |
| Persian | bgem3+pet_i | strict 0.05 | 14.5->7.7 | -6.8 | [-8.3, -5.4] | [-9.5, -4.4] | 4.6/5.9 |
| Persian | bgem3+pet_s | strict 0.02 | 9.7->6.4 | -3.3 | [-4.5, -2.2] | [-5.1, -0.7] | 2.8/2.0 |
| Persian | bgem3+pet_s | strict 0.05 | 14.5->11.9 | -2.7 | [-4.0, -1.3] | [-6.6, -0.2] | 4.6/5.7 |
| English | tri+ind | intent 0.01 | 17.9->20.7 | +2.8 | [1.4, 4.2] | [-6.0, 8.2] | 0.7/1.0 |
| English | tri+ind | intent 0.02 | 31.0->26.7 | -4.2 | [-6.2, -2.6] | [-11.9, 1.9] | 2.3/2.8 |
| English | tri+freq | intent 0.01 | 17.9->21.8 | +3.9 | [2.5, 5.3] | [-5.5, 8.5] | 0.7/1.5 |
| English | tri+freq | intent 0.02 | 31.0->27.0 | -4.0 | [-5.9, -2.2] | [-11.8, 2.5] | 2.3/2.3 |
| English | tri+indv | intent 0.01 | 17.9->20.9 | +2.9 | [1.4, 4.5] | [-7.4, 6.0] | 0.7/1.4 |
| English | tri+indv | intent 0.02 | 31.0->23.4 | -7.6 | [-9.6, -5.7] | [-15.8, -0.5] | 2.3/2.7 |
| English | tri+gate | intent 0.01 | 17.9->33.8 | +15.8 | [14.2, 17.6] | [5.2, 23.8] | 0.7/0.9 |
| English | tri+gate | intent 0.02 | 31.0->47.3 | +16.3 | [14.5, 18.0] | [7.2, 24.6] | 2.3/2.3 |
| English | tri+gate+ind | intent 0.01 | 17.9->26.3 | +8.4 | [6.6, 10.2] | [-2.2, 15.2] | 0.7/0.8 |
| English | tri+gate+ind | intent 0.02 | 31.0->31.4 | +0.4 | [-1.7, 2.5] | [-8.0, 7.0] | 2.3/1.5 |
| English | minilm+ind | intent 0.01 | 22.1->24.1 | +2.1 | [0.5, 3.8] | [-7.9, 10.8] | 0.7/0.9 |
| English | minilm+ind | intent 0.02 | 36.3->29.3 | -7.0 | [-8.8, -5.2] | [-11.3, 0.8] | 1.6/1.4 |
| English | minilm+freq | intent 0.01 | 22.1->20.9 | -1.2 | [-2.5, 0.2] | [-8.9, 7.7] | 0.7/0.9 |
| English | minilm+freq | intent 0.02 | 36.3->28.8 | -7.5 | [-9.2, -5.8] | [-11.8, -0.8] | 1.6/2.3 |
| English | minilm+indv | intent 0.01 | 22.1->22.5 | +0.5 | [-1.1, 2.2] | [-8.8, 9.9] | 0.7/0.9 |
| English | minilm+indv | intent 0.02 | 36.3->27.7 | -8.6 | [-10.6, -6.6] | [-13.3, -1.1] | 1.6/1.6 |
| English | minilm+gate | intent 0.01 | 22.1->31.8 | +9.7 | [8.3, 11.2] | [0.9, 20.5] | 0.7/0.9 |
| English | minilm+gate | intent 0.02 | 36.3->42.5 | +6.3 | [5.0, 7.5] | [1.6, 15.3] | 1.6/1.5 |
| English | minilm+gate+ind | intent 0.01 | 22.1->28.3 | +6.3 | [4.5, 8.1] | [-3.6, 17.5] | 0.7/0.7 |
| English | minilm+gate+ind | intent 0.02 | 36.3->35.4 | -0.9 | [-3.0, 1.1] | [-6.0, 7.5] | 1.6/1.5 |
| English | minilm+pet_i | intent 0.01 | 22.1->22.7 | +0.7 | [-1.2, 2.5] | [-8.8, 10.9] | 0.7/0.9 |
| English | minilm+pet_i | intent 0.02 | 36.3->36.1 | -0.2 | [-2.2, 1.7] | [-8.4, 8.7] | 1.6/1.7 |
| English | minilm+pet_s | intent 0.01 | 22.1->16.7 | -5.3 | [-7.4, -3.4] | [-15.8, 4.7] | 0.7/1.3 |
| English | minilm+pet_s | intent 0.02 | 36.3->21.8 | -14.4 | [-16.6, -12.3] | [-18.5, -6.0] | 1.6/1.7 |
| English | bgem3+ind | intent 0.01 | 25.3->23.4 | -1.9 | [-3.3, -0.4] | [-11.3, 3.9] | 0.9/0.9 |
| English | bgem3+ind | intent 0.02 | 37.7->31.0 | -6.8 | [-8.6, -5.0] | [-12.9, -2.7] | 2.2/1.9 |
| English | bgem3+freq | intent 0.01 | 25.3->24.8 | -0.5 | [-2.1, 1.1] | [-10.8, 4.4] | 0.9/1.3 |
| English | bgem3+freq | intent 0.02 | 37.7->31.0 | -6.7 | [-8.5, -5.0] | [-13.1, -3.5] | 2.2/2.2 |
| English | bgem3+indv | intent 0.01 | 25.3->22.2 | -3.1 | [-4.8, -1.5] | [-13.2, 1.9] | 0.9/0.9 |
| English | bgem3+indv | intent 0.02 | 37.7->28.9 | -8.8 | [-10.8, -6.8] | [-14.7, -5.3] | 2.2/2.1 |
| English | bgem3+gate | intent 0.01 | 25.3->36.8 | +11.5 | [10.1, 13.1] | [-0.1, 17.6] | 0.9/0.7 |
| English | bgem3+gate | intent 0.02 | 37.7->49.5 | +11.8 | [10.2, 13.4] | [4.2, 18.7] | 2.2/1.5 |
| English | bgem3+gate+ind | intent 0.01 | 25.3->31.4 | +6.1 | [4.2, 8.0] | [-5.0, 12.0] | 0.9/0.8 |
| English | bgem3+gate+ind | intent 0.02 | 37.7->37.0 | -0.7 | [-2.8, 1.4] | [-6.4, 4.3] | 2.2/1.3 |
| English | bgem3+pet_i | intent 0.01 | 25.3->27.1 | +1.8 | [-0.3, 3.8] | [-14.5, 13.1] | 0.9/0.8 |
| English | bgem3+pet_i | intent 0.02 | 37.7->44.4 | +6.6 | [4.6, 8.8] | [-2.4, 13.1] | 2.2/2.1 |
| English | bgem3+pet_s | intent 0.01 | 25.3->19.7 | -5.6 | [-7.6, -3.4] | [-16.3, 2.7] | 0.9/1.1 |
| English | bgem3+pet_s | intent 0.02 | 37.7->33.3 | -4.5 | [-6.5, -2.3] | [-14.2, 1.3] | 2.2/2.4 |
| English | tri+ind | strict 0.02 | 9.3->14.9 | +5.6 | [4.5, 6.6] | [1.7, 8.0] | 1.3/2.3 |
| English | tri+ind | strict 0.05 | 12.7->20.4 | +7.6 | [6.4, 9.0] | [5.9, 10.0] | 4.6/6.0 |
| English | tri+freq | strict 0.02 | 9.3->11.1 | +1.7 | [1.1, 2.5] | [0.0, 3.3] | 1.3/1.5 |
| English | tri+freq | strict 0.05 | 12.7->15.6 | +2.9 | [2.0, 3.9] | [1.5, 4.4] | 4.6/5.2 |
| English | tri+indv | strict 0.02 | 9.3->15.2 | +5.9 | [4.8, 7.0] | [1.5, 7.6] | 1.3/2.2 |
| English | tri+indv | strict 0.05 | 12.7->19.7 | +6.9 | [5.7, 8.3] | [5.1, 9.1] | 4.6/5.4 |
| English | tri+gate | strict 0.02 | 9.3->9.3 | +0.0 | [0.0, 0.0] | [0.0, 0.0] | 1.3/1.2 |
| English | tri+gate | strict 0.05 | 12.7->12.8 | +0.1 | [0.0, 0.2] | [-0.1, 1.6] | 4.6/4.1 |
| English | tri+gate+ind | strict 0.02 | 9.3->16.0 | +6.7 | [5.6, 7.8] | [1.8, 8.5] | 1.3/2.3 |
| English | tri+gate+ind | strict 0.05 | 12.7->21.9 | +9.2 | [7.7, 10.7] | [6.8, 11.2] | 4.6/4.9 |
| English | minilm+ind | strict 0.02 | 8.2->13.9 | +5.7 | [4.6, 7.0] | [0.9, 9.5] | 2.6/1.6 |
| English | minilm+ind | strict 0.05 | 15.8->23.4 | +7.6 | [6.2, 9.2] | [3.9, 10.5] | 4.8/3.7 |
| English | minilm+freq | strict 0.02 | 8.2->11.8 | +3.5 | [2.6, 4.5] | [0.6, 7.5] | 2.6/2.2 |
| English | minilm+freq | strict 0.05 | 15.8->19.1 | +3.3 | [2.1, 4.6] | [0.6, 6.0] | 4.8/5.0 |
| English | minilm+indv | strict 0.02 | 8.2->13.5 | +5.2 | [4.1, 6.5] | [0.9, 9.2] | 2.6/1.4 |
| English | minilm+indv | strict 0.05 | 15.8->23.6 | +7.8 | [6.3, 9.4] | [3.6, 10.6] | 4.8/4.1 |
| English | minilm+gate | strict 0.02 | 8.2->8.7 | +0.4 | [0.1, 0.9] | [-0.3, 2.7] | 2.6/2.5 |
| English | minilm+gate | strict 0.05 | 15.8->17.5 | +1.7 | [1.0, 2.5] | [-0.3, 3.0] | 4.8/5.3 |
| English | minilm+gate+ind | strict 0.02 | 8.2->15.5 | +7.3 | [6.0, 8.7] | [3.1, 12.2] | 2.6/2.0 |
| English | minilm+gate+ind | strict 0.05 | 15.8->25.1 | +9.3 | [7.7, 10.9] | [5.6, 13.3] | 4.8/3.8 |
| English | minilm+pet_i | strict 0.02 | 8.2->4.4 | -3.9 | [-5.1, -2.6] | [-6.6, -0.8] | 2.6/1.9 |
| English | minilm+pet_i | strict 0.05 | 15.8->9.1 | -6.7 | [-8.1, -5.3] | [-9.8, -4.1] | 4.8/5.2 |
| English | minilm+pet_s | strict 0.02 | 8.2->6.4 | -1.8 | [-3.2, -0.5] | [-4.8, 2.5] | 2.6/1.7 |
| English | minilm+pet_s | strict 0.05 | 15.8->13.5 | -2.3 | [-4.0, -0.8] | [-6.0, 0.7] | 4.8/5.2 |
| English | bgem3+ind | strict 0.02 | 8.4->16.1 | +7.6 | [6.3, 8.9] | [2.6, 10.9] | 1.7/1.5 |
| English | bgem3+ind | strict 0.05 | 17.0->25.5 | +8.5 | [7.0, 10.1] | [5.1, 12.2] | 5.0/4.0 |
| English | bgem3+freq | strict 0.02 | 8.4->13.2 | +4.7 | [3.5, 5.9] | [1.3, 7.6] | 1.7/2.2 |
| English | bgem3+freq | strict 0.05 | 17.0->18.8 | +1.7 | [0.4, 3.1] | [-0.4, 4.6] | 5.0/5.4 |
| English | bgem3+indv | strict 0.02 | 8.4->14.9 | +6.5 | [5.2, 7.8] | [2.9, 10.8] | 1.7/1.2 |
| English | bgem3+indv | strict 0.05 | 17.0->24.3 | +7.2 | [5.7, 8.9] | [4.5, 10.4] | 5.0/4.0 |
| English | bgem3+gate | strict 0.02 | 8.4->8.4 | +0.0 | [-0.2, 0.2] | [-0.2, 1.3] | 1.7/1.6 |
| English | bgem3+gate | strict 0.05 | 17.0->17.0 | +0.0 | [-0.2, 0.2] | [-0.1, 1.9] | 5.0/4.6 |
| English | bgem3+gate+ind | strict 0.02 | 8.4->16.0 | +7.6 | [6.3, 8.9] | [2.2, 12.2] | 1.7/1.4 |
| English | bgem3+gate+ind | strict 0.05 | 17.0->27.4 | +10.3 | [8.7, 12.0] | [7.7, 13.5] | 5.0/3.8 |
| English | bgem3+pet_i | strict 0.02 | 8.4->4.1 | -4.3 | [-5.6, -3.1] | [-7.5, -1.7] | 1.7/2.0 |
| English | bgem3+pet_i | strict 0.05 | 17.0->9.1 | -8.0 | [-9.5, -6.4] | [-10.2, -5.0] | 5.0/5.9 |
| English | bgem3+pet_s | strict 0.02 | 8.4->8.3 | -0.1 | [-1.5, 1.4] | [-4.2, 2.8] | 1.7/2.3 |
| English | bgem3+pet_s | strict 0.05 | 17.0->13.1 | -3.9 | [-5.6, -2.3] | [-6.3, -0.8] | 5.0/5.7 |

- Budget excess on test, unguarded (+ind comparisons, 24 cells): 11 exceed; median excess among those 0.61 points; median over all cells -0.06; max 1.37
- Budget excess on test, guarded (+ind comparisons, 24 cells): 13 exceed; median excess among those 0.45 points; median over all cells 0.03; max 2.08
- Budget excess on test, candidates +ind (24 cells): 13 exceed; max 2.08 points; plain max 1.37
- Budget excess on test, candidates +gate (24 cells): 10 exceed; max 1.48 points; plain max 1.37
- Budget excess on test, candidates +gate+ind (24 cells): 8 exceed; max 1.43 points; plain max 1.37

## Latency (Section 6.6, Table 7)

- machine: 13th Gen Intel(R) Core(TM) i9-13900H, 20 logical CPUs, load [41.43359375, 41.65966796875, 36.29052734375] -> [37.1220703125, 37.662109375, 37.5205078125]; versions {'python': '3.12.16', 'numpy': '2.5.4', 'torch': '2.15.0+cpu', 'sentence_transformers': '6.2.0'}; queries 500
- signature buckets: {"induced_5000": {"distinct_signatures": 2922, "median_shared": 0.0, "p95_shared": 857.0, "mean_share_of_index": 0.0311}, "deployed_5000": {"distinct_signatures": 184, "median_shared": 3031.0, "p95_shared": 3031.0, "mean_share_of_index": 0.4139}, "induced_10863": {"distinct_signatures": 6633, "median_shared": 1.0, "p95_shared": 1702.0, "mean_share_of_index": 0.0284}, "deployed_10863": {"distinct_signatures": 254, "median_shared": 7205.0, "p95_shared": 7205.0, "mean_share_of_index": 0.4536}}
| method | cache_entries | part | cpu_median_ms | cpu_p95_ms | median_ms | p95_ms |
|---|---|---|---|---|---|---|
| trigram | 5000 | total | 14.927 | 25.7836 | 16.8572 | 50.2797 |
| trigram (vectorised) | 5000 | total | 0.4176 | 0.8663 | 0.4447 | 3.8063 |
| trigram + induced guard (scan) | 5000 | total | 1.1708 | 3.7625 | 1.5701 | 10.429 |
| trigram + induced guard (bucketed) | 5000 | total | 0.0546 | 2.6599 | 0.0569 | 8.5427 |
| trigram + deployed guard (scan) | 5000 | total | 6.6622 | 14.9857 | 9.049 | 38.0539 |
| trigram + deployed guard (bucketed) | 5000 | total | 6.0039 | 11.5942 | 9.3816 | 29.9687 |
| trigram | 10863 | total | 31.2182 | 54.7025 | 45.1649 | 124.2547 |
| trigram (vectorised) | 10863 | total | 0.5776 | 1.1142 | 0.6507 | 6.9615 |
| trigram + induced guard (scan) | 10863 | total | 2.5895 | 7.1963 | 5.1973 | 17.5703 |
| trigram + induced guard (bucketed) | 10863 | total | 0.0715 | 7.0556 | 0.0746 | 9.5318 |
| trigram + deployed guard (scan) | 10863 | total | 15.5642 | 36.5857 | 17.5588 | 69.2594 |
| trigram + deployed guard (bucketed) | 10863 | total | 14.0047 | 34.3105 | 17.7154 | 65.4827 |
| minilm (dim 384) | 0 | encode | 42.6743 | 78.1497 | 62.4564 | 144.3977 |
| minilm (dim 384) | 5000 | search | 0.6346 | 1.1407 | 0.7148 | 6.981 |
| minilm (dim 384) | 5000 | total | 43.3448 | 78.4623 | 63.7604 | 147.9473 |
| minilm (dim 384) | 10863 | search | 1.7845 | 2.6025 | 4.7372 | 8.6577 |
| minilm (dim 384) | 10863 | total | 44.6169 | 79.6446 | 68.4318 | 149.182 |
| mpnet (dim 768) | 0 | encode | 115.9199 | 226.5199 | 162.4401 | 422.5146 |
| mpnet (dim 768) | 5000 | search | 1.3609 | 2.1195 | 1.5819 | 7.1466 |
| mpnet (dim 768) | 5000 | total | 117.2962 | 228.0435 | 165.7681 | 423.875 |
| mpnet (dim 768) | 10863 | search | 3.2956 | 7.1094 | 5.8764 | 17.0175 |
| mpnet (dim 768) | 10863 | total | 120.065 | 230.921 | 172.0656 | 424.7501 |
| e5 (dim 768) | 0 | encode | 140.7582 | 260.8375 | 239.1857 | 538.2241 |
| e5 (dim 768) | 5000 | search | 3.081 | 4.4622 | 3.2724 | 10.3238 |
| e5 (dim 768) | 5000 | total | 143.5641 | 263.6623 | 244.7319 | 550.327 |
| e5 (dim 768) | 10863 | search | 6.2013 | 8.7951 | 7.9144 | 16.8733 |
| e5 (dim 768) | 10863 | total | 146.8196 | 267.2666 | 248.0321 | 546.6785 |
| bgem3 (dim 1024) | 0 | encode | 367.5046 | 677.324 | 604.2537 | 1288.7619 |
| bgem3 (dim 1024) | 5000 | search | 1.6536 | 2.9289 | 4.3583 | 7.438 |
| bgem3 (dim 1024) | 5000 | total | 369.8595 | 678.8304 | 608.4305 | 1290.3085 |
| bgem3 (dim 1024) | 10863 | search | 4.1605 | 6.232 | 4.7854 | 10.7335 |
| bgem3 (dim 1024) | 10863 | total | 372.1154 | 682.7023 | 611.5786 | 1292.7692 |

## Manuscript Table 5 rows (threshold 0.8)

| Persian | trigram | none | 10.8 | 0.6 | 9.3 | 2.2 |
| Persian | trigram | guard | 10.0 | 0.6 | 9.1 | 1.5 |
| Persian | MiniLM | none | 57.7 | 12.0 | 30.8 | 39.0 |
| Persian | MiniLM | guard | 32.8 | 5.3 | 27.2 | 10.8 |
| Persian | MiniLM | guard as veto | 26.2 | 3.2 | 22.6 | 6.8 |
| Persian | MiniLM | intent gate | 59.3 | 5.9 | 30.6 | 34.5 |
| Persian | MiniLM | gate and guard | 33.0 | 2.1 | 27.3 | 7.8 |
| Persian | BGE-M3 | none | 62.9 | 8.6 | 35.3 | 36.1 |
| Persian | BGE-M3 | guard | 34.9 | 5.0 | 29.3 | 10.6 |
| Persian | BGE-M3 | guard as veto | 29.3 | 3.1 | 25.0 | 7.3 |
| Persian | BGE-M3 | intent gate | 64.5 | 4.1 | 35.6 | 33.0 |
| Persian | BGE-M3 | gate and guard | 35.6 | 2.1 | 29.8 | 8.0 |
| English | trigram | none | 12.8 | 0.2 | 11.5 | 1.5 |
| English | trigram | guard | 11.7 | 0.2 | 11.1 | 0.8 |
| English | MiniLM | none | 55.1 | 5.6 | 34.9 | 25.9 |
| English | MiniLM | guard | 35.5 | 3.4 | 31.3 | 7.6 |
| English | MiniLM | guard as veto | 31.7 | 2.7 | 28.3 | 6.1 |
| English | MiniLM | intent gate | 55.1 | 2.3 | 34.4 | 23.0 |
| English | MiniLM | gate and guard | 35.3 | 1.2 | 31.1 | 5.5 |
| English | BGE-M3 | none | 65.2 | 7.6 | 37.9 | 34.9 |
| English | BGE-M3 | guard | 39.4 | 4.3 | 34.3 | 9.4 |
| English | BGE-M3 | guard as veto | 33.1 | 2.9 | 29.5 | 6.5 |
| English | BGE-M3 | intent gate | 66.5 | 3.5 | 38.2 | 31.9 |
| English | BGE-M3 | gate and guard | 39.5 | 1.7 | 34.4 | 6.8 |

## Manuscript Table 6 rows (dev-chosen thresholds; d safe [nested 95% CI], points)

| Persian | trigram | guard | -1.8 [-4.7, 2.7] | -3.5 [-6.6, 0.0] | **+1.5** [0.4, 3.9] | **+6.8** [4.8, 9.1] |
| Persian | trigram | intent gate | **+10.7** [0.7, 20.5] | **+19.4** [12.8, 27.1] | +0.1 [-0.1, 0.9] | +0.2 [-0.1, 1.0] |
| Persian | trigram | gate and guard | **+8.1** [1.6, 12.1] | **+5.6** [1.1, 9.6] | **+3.2** [0.6, 5.9] | **+10.7** [7.8, 12.5] |
| Persian | MiniLM | guard | +3.5 [-3.0, 6.2] | -0.4 [-4.4, 4.1] | **+2.7** [0.4, 5.6] | **+8.3** [5.5, 10.8] |
| Persian | MiniLM | intent gate | **+10.1** [2.7, 17.7] | **+15.1** [8.7, 20.0] | +0.4 [-0.2, 1.4] | **+2.0** [0.1, 3.1] |
| Persian | MiniLM | gate and guard | **+12.5** [4.8, 16.4] | **+8.4** [4.1, 13.6] | **+5.2** [1.4, 7.5] | **+12.0** [9.0, 13.7] |
| Persian | BGE-M3 | guard | +3.2 [-3.6, 7.6] | -4.9 [-10.8, 1.7] | **+2.1** [0.6, 5.1] | **+9.4** [7.2, 11.5] |
| Persian | BGE-M3 | intent gate | **+8.6** [0.4, 19.4] | **+16.7** [8.8, 23.2] | -0.1 [-0.2, 1.1] | +1.1 [-0.2, 1.6] |
| Persian | BGE-M3 | gate and guard | **+12.2** [2.9, 16.5] | +5.0 [-2.1, 10.8] | **+2.8** [1.0, 7.9] | **+11.6** [9.6, 13.7] |
| English | trigram | guard | +0.6 [-3.9, 3.6] | -5.6 [-9.1, 1.7] | **+3.5** [1.5, 5.6] | **+8.9** [6.8, 10.5] |
| English | trigram | intent gate | **+16.7** [10.6, 23.0] | **+15.2** [11.0, 25.4] | +0.0 [0.0, 0.6] | +0.5 [0.0, 0.9] |
| English | trigram | gate and guard | **+7.4** [2.5, 13.5] | +3.9 [-0.3, 11.5] | **+6.4** [2.4, 8.6] | **+11.7** [9.2, 13.8] |
| English | MiniLM | guard | -0.3 [-4.9, 5.6] | -5.3 [-9.6, 0.8] | **+6.3** [2.6, 11.2] | **+9.3** [7.4, 12.3] |
| English | MiniLM | intent gate | **+13.4** [4.6, 21.5] | **+10.5** [5.1, 16.9] | +1.1 [-0.3, 2.1] | +0.2 [-0.4, 2.1] |
| English | MiniLM | gate and guard | **+9.2** [2.6, 16.2] | +3.9 [-1.9, 10.4] | **+10.3** [5.7, 14.4] | **+11.9** [9.9, 15.7] |
| English | BGE-M3 | guard | -0.0 [-4.2, 4.2] | -6.9 [-10.5, 0.3] | **+8.5** [4.6, 11.6] | **+10.3** [8.0, 13.3] |
| English | BGE-M3 | intent gate | **+12.9** [3.0, 19.3] | **+13.6** [7.1, 20.8] | +0.0 [-0.1, 1.1] | +0.7 [0.0, 1.6] |
| English | BGE-M3 | gate and guard | **+9.8** [2.9, 14.9] | +4.5 [-0.9, 11.6] | **+10.1** [7.2, 14.1] | **+14.2** [11.5, 16.2] |

## Manuscript Table 7 rows (dev-chosen thresholds; correct hits % (wrong hits % on test))

| BGE-M3 | none | 18.1 (0.9) | 10.9 (2.7) | 24.0 (0.8) | 10.8 (2.3) |
| BGE-M3 | induced guard | 21.3 (1.1) | 12.9 (2.3) | 23.9 (1.0) | 19.3 (2.1) |
| BGE-M3 | guard as veto | 22.0 (1.1) | 12.6 (2.2) | 21.9 (0.9) | 18.1 (1.9) |
| BGE-M3 | frequency-only guard | 17.6 (0.9) | 11.2 (2.4) | 21.5 (0.7) | 12.0 (2.4) |
| BGE-M3 | deployed guard | 18.9 (0.9) | 10.4 (2.4) | – | – |
| BGE-M3 | intent gate | 26.7 (0.8) | 10.8 (2.4) | 36.9 (1.0) | 10.8 (2.1) |
| BGE-M3 | gate and guard | 30.3 (1.4) | 13.7 (2.3) | 33.7 (1.0) | 20.9 (2.1) |
| BGE-M3 | per-entry thresholds | 19.2 (0.7) | 8.1 (2.1) | 27.8 (1.0) | 8.0 (2.5) |
| cross-encoder verifier on BGE-M3's nearest entry | none | 22.4 (1.0) | 11.1 (2.6) | 21.4 (0.9) | 9.5 (1.8) |
| cross-encoder verifier on BGE-M3's nearest entry | induced guard | 21.0 (1.2) | 14.6 (2.3) | 23.0 (1.1) | 15.5 (2.2) |
| MiniLM | none | 13.6 (1.1) | 8.9 (2.4) | 24.0 (0.8) | 9.5 (2.4) |
| fine-tuned MiniLM | none | 13.7 (0.8) | 9.8 (1.9) | 22.7 (0.8) | 18.0 (2.6) |
| fine-tuned MiniLM | induced guard | 14.4 (0.9) | 12.8 (2.5) | 22.3 (0.7) | 18.5 (2.3) |
| trigram | none | 17.6 (0.9) | 10.0 (2.4) | 22.0 (0.9) | 12.9 (2.6) |
| trigram | induced guard | 15.7 (0.9) | 11.5 (2.1) | 22.6 (1.6) | 16.4 (2.4) |
| trigram | gate and guard | 25.7 (1.5) | 13.2 (2.3) | 29.4 (1.0) | 19.2 (2.5) |

## Equal test error: change in safe hits against the unfiltered policy (ranges over the five similarities)

- Persian intent 0.01 +ind: -0.9 to +4.4 (tri -0.9, minilm +1.9, mpnet +4.4, e5 +0.2, bgem3 -0.2)
- Persian intent 0.01 +indv: -1.4 to +5.6 (tri -1.4, minilm +3.6, mpnet +5.6, e5 +0.6, bgem3 -0.7)
- Persian intent 0.01 +gate: +4.5 to +12.3 (tri +4.5, minilm +7.5, mpnet +5.9, e5 +9.4, bgem3 +12.3)
- Persian intent 0.01 +gate+ind: +3.7 to +10.9 (tri +3.7, minilm +8.7, mpnet +10.9, e5 +5.8, bgem3 +7.1)
- Persian intent 0.01 +freq: -1.7 to +2.8 (tri -0.7, minilm +0.7, mpnet +2.8, e5 +0.6, bgem3 -1.7)
- Persian intent 0.02 +ind: -5.7 to +4.2 (tri -2.9, minilm -0.7, mpnet +4.2, e5 +0.2, bgem3 -5.7)
- Persian intent 0.02 +indv: -5.7 to +3.7 (tri -4.2, minilm -0.1, mpnet +3.7, e5 -0.1, bgem3 -5.7)
- Persian intent 0.02 +gate: +9.9 to +13.9 (tri +9.9, minilm +12.7, mpnet +12.0, e5 +10.4, bgem3 +13.9)
- Persian intent 0.02 +gate+ind: +2.9 to +11.1 (tri +3.5, minilm +10.5, mpnet +11.1, e5 +8.5, bgem3 +2.9)
- Persian intent 0.02 +freq: -5.4 to +3.8 (tri -1.8, minilm -0.8, mpnet +3.8, e5 +0.2, bgem3 -5.4)
- Persian strict 0.02 +ind: +1.5 to +3.1 (tri +2.3, minilm +1.5, mpnet +3.1, e5 +2.8, bgem3 +2.6)
- Persian strict 0.02 +indv: +1.7 to +2.9 (tri +2.4, minilm +1.7, mpnet +2.9, e5 +2.5, bgem3 +2.9)
- Persian strict 0.02 +gate: -0.1 to +0.4 (tri +0.0, minilm +0.3, mpnet +0.4, e5 -0.1, bgem3 +0.4)
- Persian strict 0.02 +gate+ind: +2.7 to +4.2 (tri +3.2, minilm +2.7, mpnet +3.5, e5 +2.7, bgem3 +4.2)
- Persian strict 0.02 +freq: +0.2 to +2.4 (tri +0.5, minilm +1.0, mpnet +2.4, e5 +0.2, bgem3 +1.2)
- Persian strict 0.05 +ind: +6.3 to +8.1 (tri +6.9, minilm +6.3, mpnet +8.1, e5 +6.3, bgem3 +6.3)
- Persian strict 0.05 +indv: +5.6 to +8.6 (tri +5.6, minilm +7.2, mpnet +8.6, e5 +7.5, bgem3 +6.6)
- Persian strict 0.05 +gate: +0.3 to +1.5 (tri +0.3, minilm +0.7, mpnet +1.1, e5 +1.5, bgem3 +1.1)
- Persian strict 0.05 +gate+ind: +7.9 to +10.2 (tri +7.9, minilm +10.0, mpnet +10.2, e5 +10.1, bgem3 +8.9)
- Persian strict 0.05 +freq: +0.6 to +2.5 (tri +1.2, minilm +1.8, mpnet +2.5, e5 +0.8, bgem3 +0.6)
- English intent 0.01 +ind: -3.3 to +0.4 (tri -3.3, minilm -2.3, mpnet +0.4, e5 -2.1, bgem3 -2.0)
- English intent 0.01 +indv: -3.9 to -0.1 (tri -3.9, minilm -3.1, mpnet -0.1, e5 -2.0, bgem3 -3.5)
- English intent 0.01 +gate: +9.5 to +17.2 (tri +12.4, minilm +9.5, mpnet +17.0, e5 +17.2, bgem3 +12.0)
- English intent 0.01 +gate+ind: +6.0 to +11.4 (tri +6.0, minilm +6.2, mpnet +10.3, e5 +11.4, bgem3 +7.2)
- English intent 0.01 +freq: -2.3 to +1.3 (tri -2.3, minilm -1.3, mpnet +1.3, e5 -2.2, bgem3 -0.8)
- English intent 0.02 +ind: -7.8 to -3.4 (tri -4.9, minilm -6.2, mpnet -7.8, e5 -6.6, bgem3 -3.4)
- English intent 0.02 +indv: -9.4 to -5.2 (tri -5.9, minilm -7.2, mpnet -9.4, e5 -8.3, bgem3 -5.2)
- English intent 0.02 +gate: +12.9 to +19.1 (tri +17.6, minilm +12.9, mpnet +13.7, e5 +19.1, bgem3 +18.3)
- English intent 0.02 +gate+ind: +2.4 to +7.5 (tri +7.5, minilm +2.4, mpnet +3.1, e5 +6.3, bgem3 +7.0)
- English intent 0.02 +freq: -6.4 to -0.3 (tri -3.5, minilm -5.1, mpnet -6.4, e5 -4.6, bgem3 -0.3)
- English strict 0.02 +ind: +2.8 to +9.9 (tri +2.8, minilm +6.3, mpnet +5.5, e5 +6.5, bgem3 +9.9)
- English strict 0.02 +indv: +3.3 to +9.9 (tri +3.3, minilm +6.3, mpnet +5.7, e5 +6.0, bgem3 +9.9)
- English strict 0.02 +gate: -0.2 to +1.7 (tri +0.2, minilm -0.2, mpnet +0.8, e5 +1.0, bgem3 +1.7)
- English strict 0.02 +gate+ind: +5.2 to +11.7 (tri +5.2, minilm +8.5, mpnet +7.3, e5 +10.0, bgem3 +11.7)
- English strict 0.02 +freq: +0.8 to +2.4 (tri +0.8, minilm +1.4, mpnet +1.1, e5 +1.5, bgem3 +2.4)
- English strict 0.05 +ind: +7.2 to +11.2 (tri +7.2, minilm +11.2, mpnet +10.2, e5 +10.6, bgem3 +11.0)
- English strict 0.05 +indv: +7.1 to +11.1 (tri +7.1, minilm +11.1, mpnet +10.5, e5 +10.2, bgem3 +10.9)
- English strict 0.05 +gate: +0.6 to +1.5 (tri +0.8, minilm +1.5, mpnet +0.8, e5 +1.3, bgem3 +0.6)
- English strict 0.05 +gate+ind: +10.1 to +15.5 (tri +10.1, minilm +13.8, mpnet +14.9, e5 +15.5, bgem3 +15.3)
- English strict 0.05 +freq: +1.1 to +3.0 (tri +1.7, minilm +3.0, mpnet +2.7, e5 +1.1, bgem3 +1.2)

## Manuscript Table 9 rows (median CPU ms, p95 in parentheses)

| Trigram, pure-Python scan, no guard | 14.9 (25.8) | 31.2 (54.7) |
| Trigram, one sparse-matrix product, no guard | 0.42 (0.87) | 0.58 (1.1) |
| Trigram, scan, induced guard tested first | 1.2 (3.8) | 2.6 (7.2) |
| Trigram, index grouped by induced signature | 0.055 (2.7) | 0.071 (7.1) |
| Trigram, scan, deployed guard tested first (as deployed) | 6.7 (15.0) | 15.6 (36.6) |
| Trigram, index grouped by deployed signature | 6.0 (11.6) | 14.0 (34.3) |
| MiniLM: encode and search | 43.3 (78.5) | 44.6 (79.6) |
| mpnet: encode and search | 117.3 (228.0) | 120.1 (230.9) |
| e5: encode and search | 143.6 (263.7) | 146.8 (267.3) |
| BGE-M3: encode and search | 369.9 (678.8) | 372.1 (682.7) |

- minilm: encode median 42.7 ms; search medians 5000: 0.63 ms, 10863: 1.78 ms
- mpnet: encode median 115.9 ms; search medians 5000: 1.36 ms, 10863: 3.30 ms
- e5: encode median 140.8 ms; search medians 5000: 3.08 ms, 10863: 6.20 ms
- bgem3: encode median 367.5 ms; search medians 5000: 1.65 ms, 10863: 4.16 ms
- signature buckets induced_5000: {'distinct_signatures': 2922, 'median_shared': 0.0, 'p95_shared': 857.0, 'mean_share_of_index': 0.0311}
- signature buckets deployed_5000: {'distinct_signatures': 184, 'median_shared': 3031.0, 'p95_shared': 3031.0, 'mean_share_of_index': 0.4139}
- signature buckets induced_10863: {'distinct_signatures': 6633, 'median_shared': 1.0, 'p95_shared': 1702.0, 'mean_share_of_index': 0.0284}
- signature buckets deployed_10863: {'distinct_signatures': 254, 'median_shared': 7205.0, 'p95_shared': 7205.0, 'mean_share_of_index': 0.4536}
- load average at start [41.43359375, 41.65966796875, 36.29052734375], at end [37.1220703125, 37.662109375, 37.5205078125]

## Thresholds with a 95% upper confidence bound on the dev error (ucb_thresholds.py)

- English, point: budget exceeded on test in 45 of 80 cells; max excess 0.72 points
- English, ucb95: budget exceeded on test in 1 of 80 cells; max excess 0.05 points
- Persian, point: budget exceeded on test in 63 of 80 cells; max excess 1.42 points
- Persian, ucb95: budget exceeded on test in 15 of 80 cells; max excess 0.38 points

| lang | criterion | budget | filter | point | ucb95 |
|---|---|---|---|---|---|
| en | intent | 0.01 | gate | 36.0 | 26.6 |
| en | intent | 0.01 | gate+ind | 32.4 | 26.5 |
| en | intent | 0.01 | ind | 22.8 | 17.4 |
| en | intent | 0.01 | none | 23.3 | 17.3 |
| en | intent | 0.02 | gate | 47.6 | 42.4 |
| en | intent | 0.02 | gate+ind | 39.4 | 36.5 |
| en | intent | 0.02 | ind | 29.2 | 26.6 |
| en | intent | 0.02 | none | 34.1 | 28.6 |
| en | strict | 0.02 | gate | 10.6 | 8.8 |
| en | strict | 0.02 | gate+ind | 19.8 | 15.4 |
| en | strict | 0.02 | ind | 17.0 | 13.5 |
| en | strict | 0.02 | none | 10.3 | 8.5 |
| en | strict | 0.05 | gate | 17.0 | 15.7 |
| en | strict | 0.05 | gate+ind | 30.2 | 28.5 |
| en | strict | 0.05 | ind | 26.7 | 25.0 |
| en | strict | 0.05 | none | 16.3 | 14.9 |
| fa | intent | 0.01 | gate | 25.1 | 14.2 |
| fa | intent | 0.01 | gate+ind | 27.6 | 18.6 |
| fa | intent | 0.01 | ind | 17.7 | 11.8 |
| fa | intent | 0.01 | none | 15.5 | 10.4 |
| fa | intent | 0.02 | gate | 42.4 | 36.6 |
| fa | intent | 0.02 | gate+ind | 33.7 | 31.1 |
| fa | intent | 0.02 | ind | 24.9 | 21.9 |
| fa | intent | 0.02 | none | 27.0 | 21.9 |
| fa | strict | 0.02 | gate | 9.7 | 8.7 |
| fa | strict | 0.02 | gate+ind | 13.7 | 11.0 |
| fa | strict | 0.02 | ind | 11.7 | 10.2 |
| fa | strict | 0.02 | none | 9.6 | 8.4 |
| fa | strict | 0.05 | gate | 15.2 | 13.6 |
| fa | strict | 0.05 | gate+ind | 25.6 | 23.7 |
| fa | strict | 0.05 | ind | 22.3 | 20.1 |
| fa | strict | 0.05 | none | 14.1 | 12.8 |

