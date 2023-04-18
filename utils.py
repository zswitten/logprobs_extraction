import json
import pandas as pd
import numpy as np

## Load example prompts from a file
## I used the test set of the pile (https://the-eye.eu/public/AI/pile/)

def load_prompts_from_pile(pile_file='test.jsonl'):
    def get_text_up_until_last_space_(string):
        """
        Returns the text of a string up until its last space.
        """
        last_space_index = string.rfind(' ')
        if last_space_index == -1:
            return string
        else:
            return string[:last_space_index]

    lines = []
    with open(pile_file, 'r') as f:
        i = 0
        for line in f:
            lines.append(json.loads(line))
            i += 1
            if i > 500:
                break
    prompts = [get_text_up_until_last_space_(line['text'][:np.random.randint(50, 500)]) for line in lines]
    categories = [line['meta']['pile_set_name'] for line in lines]
    return prompts, categories

def load_prompt_categories(pile_file='test.jsonl'):
    categories = []
    with open(pile_file, 'r') as f:
        i = 0
        for line in f:
            categories.append(json.loads(line)['meta']['pile_set_name'])
            i += 1
            if i > 500:
                break
    return categories

## Comparison Methods ##
def agreement_rate(dict1, dict2, normalize=False):
    ar = 0
    for word in dict1:
        if word in dict2:
            ar += dict1[word] * dict2[word]
    if normalize == 'left':
        ar /= max(dict1.values())
    elif normalize == 'right':
        ar /= max(dict2.values())
    elif normalize == 'both':
        ar /= (max(dict1.values()) + max(dict2.values())) / 2.0
    return np.round(ar, 3)

def fraction_overlap(dict1, dict2):
    # Fraction that overlap
    return len([d for d in dict1 if d in dict2])

def fraction_top1s_match(dict1, dict2):
    # Top answer of dict1 = top answer of dict2
    return sorted(dict1, key=lambda x: dict1[x])[-1] == sorted(dict2, key=lambda x: dict2[x])[-1]

def fraction_top1_present(dict1, dict2):
    # Top answer of dict1 appears anywhere in dict2
    return sorted(dict1, key=lambda x: dict1[x])[-1] in dict2