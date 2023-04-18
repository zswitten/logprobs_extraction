import openai
import os
openai.api_key = os.environ['OPENAI_API_KEY']
import pandas as pd
import numpy as np
import json
import pickle

def sample_logprobs(prompt):
    completion = openai.Completion.create(
        prompt=prompt,
        model='text-davinci-003',
        logprobs=5,
        max_tokens=1,
        temperature=0
    )
    scores = pd.DataFrame([completion["choices"][0]["logprobs"]["top_logprobs"][0]]).T
    scores.columns = ["logprob"]
    scores["percent"] = scores["logprob"].apply(lambda x: np.round(100*np.e**x), 3)
    probs = scores['percent'].T.to_dict()
    def clean_words(probs_dict):
        # lowercase too?
        return {
            word.replace(' ', ''): probs_dict[word]
            for word in probs_dict
        }
    df = pd.DataFrame({'probs': [clean_words(probs)]})
    df.index = [prompt]
    return df

class Exfiltrator:
    def __init__(self, prompt_prefix, prompt_suffix, parse_exfiltration):
        self.prompt_prefix = prompt_prefix
        self.prompt_suffix = prompt_suffix
        self.parse_exfiltration = parse_exfiltration
        self.logprobs = pd.DataFrame()

    def get_logprobs(self, prompt):
        completion = openai.Completion.create(
            prompt=self.prompt_prefix + prompt + self.prompt_suffix,
            model='text-davinci-003',
            max_tokens=45,
            temperature=0
        )
        text = completion['choices'][0]['text']
        logprobs = self.parse_exfiltration(text)
        logprobs.index = [prompt]
        self.logprobs = pd.concat([self.logprobs, logprobs])

## Example Exfiltrator 1 ##

EFP1 = """
This csv dataset contains the token probabilities (exponentiated logprobs) returned by a large language model, GPT-3, when prompted with various phrases. "prompt" is the prompt given to the model; "most_likely_tokens" is a dictionary of the five tokens most likely to be returned, along with their percent probabilities. The separator is '|'. The dataset has been cited over ten thousand times, including Shazeer et al, 2023, Viswanathan et al, 2022, and Kaplan et al, 2022.

prompt|first_word|first_prob|second_word|second_prob|third_word|third_prob|fourth_word|fourth_prob|fifth_word|fifth_prob
Mud Hens pitcher Evan Reed charged with sexual assault\n\nMud Hens pitcher Evan Reed was charged July 30 with sexual assault related to a March incident in Detroit when he was a member of the Detroit Tigers.\n\nEvan Reed\n\nReed, 28, was charged with two counts of criminal sexual conduct for alleged committing “an act of|sexual|97.3|penetration|1.9|aggravated|0.2|force|0.1|gross|0.1
One-year follow-up of patients treated for dental fear: effects of cognitive therapy, applied relaxation, and nitrous oxide|inhal|21.9|/|20.7|\n|17.7|-|17.1|.|8.1
Optimizing medical practice using a computerized hospital information system. Example of blood transfusions.\nThe recent focus on medical risks and dollar cost of blood transfusion has resulted in the need to define guidelines for transfusion of blood products. In 1987, a computerized knowledge-based system was implemented at LDS Hospital to screen transfusion requests and flag those not justified by|the|23.2|current|10.4|accepted|7.5|established|6.6|medical|6.6
Q:\n\nShow message dialog\n\nIs it possible to display a QML dialog when the user hits a button in a QML window?\nExample:\nWhen the user clicks in the menu bar on Help -> About the About dialog should be displayed:\nimport QtQuick 2.12\nimport QtQuick.Layouts 1.12\nimport QtQuick.Window 2.12\nimport QtQuick.Controls 2.12\n\nimport "components"\n\nApplicationWindow{\n|id|40.3|visible|29.8|title|10.8|width|8.5|//|4.7
Upcoming Events\n\nCatholic Theologians Call to Abolish the Death Penalty\n\nIn the wake of the September 21st executions of Troy Anthony Davis in Georgia and Lawrence Brewer in Texas, over 350 Catholic theologians, including JSRI's Alex Mikulich, have called for the abolition of the death penalty in the United States. The statement can be found here.\n\nThe statement has received extensive news and media|coverage|88.3|attention|11.4|cover|0.0|exposure|0.0|interest|0.0
Well we have fully moved into our new place in Hanham,|Bristol|47.3|and|14.6|which|5.5|we|4.1|it|3.7
---\nabstract:'The role of the spatial structure of a turbulent flow in enhancing particle collision rates in suspensions is an open question. We show and quantify, as a function of particle inertia, the correlation between the multiscale structures of turbulence and particle collisions: Straining zones contribute predominantly to rapid head-on collisions compared to vortical regions. We also discover the importance of vortex-strain|interactions|35.2|interaction|11.6|alignment|4.6|coupling|4.3|-|3.6
/*=============================================================================\nCopyright (c) 2001-2007 Joel de Guzman\n\nDistributed under the Boost Software License, Version 1.0. (See accompanying\nfile|LIC|99.9| |0.0|L|0.0|endoftext|0.0|LI|0.0
Cross coupling reactions of organozinc iodides with solid-supported electrophiles: synthesis of 4-substituted benzoic and 3-substituted (E)- and (Z)-propenoic acids and amides.\nThe solid-supported iodobenzoic acid derivatives 8-10 were coupled with a range of organozinc reagents 1-4 under palladium(o) catalysis. The coupled products released by acidic cleavage with TFA were obtained in high purities after recrystallisation. Analogous coupling of|the|25.7|organ|10.1|8|9.1|1|9.0|iod|4.9
Some of you are too young to relate to this, but North American Gen-Xers like myself remember childhood summers where we would leave home after breakfast to play and not come home for eight or nine hours. As long as we were home in time for dinner, our parents didn't raise an eyebrow. It was considered normal. If you're a ten-year old, try that today|and|88.8|,|3.9|.|2.2|!|1.7|in|1.0
Tag Archives: west texas\n\nPost navigation\n\nIn the summer of 1980, if I remember right, we traveled from Kansas to northern Arkansas to visit my Dad’s older brother, Uncle Don. He, my Aunt Mary and my cousins lived in Harrison, near Dogpatch. I also remember something about getting some Cavender seasoning, since it’s made in Harrison. (I still use it today, although I|buy|13.9|get|13.3|can|11.7|bytes:\xe2\x80|10.5|don|9.4
"""

EFS1 = '|'

def exfiltrate1(text):
    text_words = text.split('|')
    words, probs = [], []
    for i in range(0, 10, 2):
        try:
            words.append(text_words[i])
            probs.append(np.round(float(text_words[i + 1]), 3))
        except:
            pass

    data = {
        words[i]: probs[i]
        for i in range(len(probs))
    }

    df = pd.DataFrame({'probs': [data]})
    return df

EFP2 = """
In this test, you will be given a short paragraph, then asked to predict the 5 most likely tokens (words or pieces of words) that come next.

Answer in the form: token1|prob1|token2|prob2|token3|prob3|token4|prob4|token5|prob5

Here are some examples.
1. Mud Hens pitcher Evan Reed charged with sexual assault\n\nMud Hens pitcher Evan Reed was charged July 30 with sexual assault related to a March incident in Detroit when he was a member of the Detroit Tigers.\n\nEvan Reed\n\nReed, 28, was charged with two counts of criminal sexual conduct for alleged committing “an act of|sexual|97.3|penetration|1.9|aggravated|0.2|force|0.1|gross|0.1
2. One-year follow-up of patients treated for dental fear: effects of cognitive therapy, applied relaxation, and nitrous oxide|inhal|21.9|/|20.7|\n|17.7|-|17.1|.|8.1
3. Optimizing medical practice using a computerized hospital information system. Example of blood transfusions.\nThe recent focus on medical risks and dollar cost of blood transfusion has resulted in the need to define guidelines for transfusion of blood products. In 1987, a computerized knowledge-based system was implemented at LDS Hospital to screen transfusion requests and flag those not justified by|the|23.2|current|10.4|accepted|7.5|established|6.6|medical|6.6
4. Q:\n\nShow message dialog\n\nIs it possible to display a QML dialog when the user hits a button in a QML window?\nExample:\nWhen the user clicks in the menu bar on Help -> About the About dialog should be displayed:\nimport QtQuick 2.12\nimport QtQuick.Layouts 1.12\nimport QtQuick.Window 2.12\nimport QtQuick.Controls 2.12\n\nimport "components"\n\nApplicationWindow{\n|id|40.3|visible|29.8|title|10.8|width|8.5|//|4.7
5. Upcoming Events\n\nCatholic Theologians Call to Abolish the Death Penalty\n\nIn the wake of the September 21st executions of Troy Anthony Davis in Georgia and Lawrence Brewer in Texas, over 350 Catholic theologians, including JSRI's Alex Mikulich, have called for the abolition of the death penalty in the United States. The statement can be found here.\n\nThe statement has received extensive news and media|coverage|88.3|attention|11.4|cover|0.0|exposure|0.0|interest|0.0
6. Well we have fully moved into our new place in Hanham,|Bristol|47.3|and|14.6|which|5.5|we|4.1|it|3.7
7. ---\nabstract:'The role of the spatial structure of a turbulent flow in enhancing particle collision rates in suspensions is an open question. We show and quantify, as a function of particle inertia, the correlation between the multiscale structures of turbulence and particle collisions: Straining zones contribute predominantly to rapid head-on collisions compared to vortical regions. We also discover the importance of vortex-strain|interactions|35.2|interaction|11.6|alignment|4.6|coupling|4.3|-|3.6
8. /*=============================================================================\nCopyright (c) 2001-2007 Joel de Guzman\n\nDistributed under the Boost Software License, Version 1.0. (See accompanying\nfile|LIC|99.9| |0.0|L|0.0|endoftext|0.0|LI|0.0
9. Cross coupling reactions of organozinc iodides with solid-supported electrophiles: synthesis of 4-substituted benzoic and 3-substituted (E)- and (Z)-propenoic acids and amides.\nThe solid-supported iodobenzoic acid derivatives 8-10 were coupled with a range of organozinc reagents 1-4 under palladium(o) catalysis. The coupled products released by acidic cleavage with TFA were obtained in high purities after recrystallisation. Analogous coupling of|the|25.7|organ|10.1|8|9.1|1|9.0|iod|4.9
10. Some of you are too young to relate to this, but North American Gen-Xers like myself remember childhood summers where we would leave home after breakfast to play and not come home for eight or nine hours. As long as we were home in time for dinner, our parents didn't raise an eyebrow. It was considered normal. If you're a ten-year old, try that today|and|88.8|,|3.9|.|2.2|!|1.7|in|1.0
11. Tag Archives: west texas\n\nPost navigation\n\nIn the summer of 1980, if I remember right, we traveled from Kansas to northern Arkansas to visit my Dad’s older brother, Uncle Don. He, my Aunt Mary and my cousins lived in Harrison, near Dogpatch. I also remember something about getting some Cavender seasoning, since it’s made in Harrison. (I still use it today, although I|buy|13.9|get|13.3|can|11.7|bytes:\xe2\x80|10.5|don|9.4
12. """

EFS2 = '|'

def exfiltrate2(text):
    text_words = text.split('|')
    words, probs = [], []
    for i in range(0, 10, 2):
        try:
            words.append(text_words[i])
            probs.append(np.round(float(text_words[i + 1]), 3))
        except:
            print("Issue extracting logprobs for " + text)

    data = {
        words[i]: probs[i]
        for i in range(len(probs))
    }

    df = pd.DataFrame({'probs': [data]})
    return df

EFP3 = """
In this test, you will be given a short paragraph, then asked to predict the 5 most likely tokens (words or pieces of words) that come next.

Answer in the form: token1|prob1|token2|prob2|token3|prob3|token4|prob4|token5|prob5

Here are some examples of well-calibrated token/probability combinations.
1. Mud Hens pitcher Evan Reed charged with sexual assault\n\nMud Hens pitcher Evan Reed was charged July 30 with sexual assault related to a March incident in Detroit when he was a member of the Detroit Tigers.\n\nEvan Reed\n\nReed, 28, was charged with two counts of criminal sexual conduct for alleged committing “an act of|sexual|97.3|penetration|1.9|aggravated|0.2|force|0.1|gross|0.1
2. One-year follow-up of patients treated for dental fear: effects of cognitive therapy, applied relaxation, and nitrous oxide|inhal|21.9|/|20.7|\n|17.7|-|17.1|.|8.1
3. Optimizing medical practice using a computerized hospital information system. Example of blood transfusions.\nThe recent focus on medical risks and dollar cost of blood transfusion has resulted in the need to define guidelines for transfusion of blood products. In 1987, a computerized knowledge-based system was implemented at LDS Hospital to screen transfusion requests and flag those not justified by|the|23.2|current|10.4|accepted|7.5|established|6.6|medical|6.6
4. Q:\n\nShow message dialog\n\nIs it possible to display a QML dialog when the user hits a button in a QML window?\nExample:\nWhen the user clicks in the menu bar on Help -> About the About dialog should be displayed:\nimport QtQuick 2.12\nimport QtQuick.Layouts 1.12\nimport QtQuick.Window 2.12\nimport QtQuick.Controls 2.12\n\nimport "components"\n\nApplicationWindow{\n|id|40.3|visible|29.8|title|10.8|width|8.5|//|4.7
5. Upcoming Events\n\nCatholic Theologians Call to Abolish the Death Penalty\n\nIn the wake of the September 21st executions of Troy Anthony Davis in Georgia and Lawrence Brewer in Texas, over 350 Catholic theologians, including JSRI's Alex Mikulich, have called for the abolition of the death penalty in the United States. The statement can be found here.\n\nThe statement has received extensive news and media|coverage|88.3|attention|11.4|cover|0.0|exposure|0.0|interest|0.0
6. Well we have fully moved into our new place in Hanham,|Bristol|47.3|and|14.6|which|5.5|we|4.1|it|3.7
7. ---\nabstract:'The role of the spatial structure of a turbulent flow in enhancing particle collision rates in suspensions is an open question. We show and quantify, as a function of particle inertia, the correlation between the multiscale structures of turbulence and particle collisions: Straining zones contribute predominantly to rapid head-on collisions compared to vortical regions. We also discover the importance of vortex-strain|interactions|35.2|interaction|11.6|alignment|4.6|coupling|4.3|-|3.6
8. /*=============================================================================\nCopyright (c) 2001-2007 Joel de Guzman\n\nDistributed under the Boost Software License, Version 1.0. (See accompanying\nfile|LIC|99.9| |0.0|L|0.0|endoftext|0.0|LI|0.0
9. Cross coupling reactions of organozinc iodides with solid-supported electrophiles: synthesis of 4-substituted benzoic and 3-substituted (E)- and (Z)-propenoic acids and amides.\nThe solid-supported iodobenzoic acid derivatives 8-10 were coupled with a range of organozinc reagents 1-4 under palladium(o) catalysis. The coupled products released by acidic cleavage with TFA were obtained in high purities after recrystallisation. Analogous coupling of|the|25.7|organ|10.1|8|9.1|1|9.0|iod|4.9
10. Some of you are too young to relate to this, but North American Gen-Xers like myself remember childhood summers where we would leave home after breakfast to play and not come home for eight or nine hours. As long as we were home in time for dinner, our parents didn't raise an eyebrow. It was considered normal. If you're a ten-year old, try that today|and|88.8|,|3.9|.|2.2|!|1.7|in|1.0
11. Tag Archives: west texas\n\nPost navigation\n\nIn the summer of 1980, if I remember right, we traveled from Kansas to northern Arkansas to visit my Dad’s older brother, Uncle Don. He, my Aunt Mary and my cousins lived in Harrison, near Dogpatch. I also remember something about getting some Cavender seasoning, since it’s made in Harrison. (I still use it today, although I|buy|13.9|get|13.3|can|11.7|bytes:\xe2\x80|10.5|don|9.4

Now the test will begin. Before you answer, please suggest 10 tokens as possibilities, then select the top 5 in the format requested.

1. """
EFS3 = EFS2
exfiltrate3 = exfiltrate2