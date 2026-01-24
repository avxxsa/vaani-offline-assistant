---
datasets:
- openslr
language:
- ne
metrics:
- cer
- wer
---

# Model Card for wav2vec2-nepali

<!-- Provide a quick summary of what the model is/does. -->

wav2vec2-nepali is the fine-tuned model for Nepali language, developed by finetuning the Facebook's wav2vec2 speech recognition model

## Model Details
This model is fine-tuned on Nepali language dataset, so it can be used for transcribing Nepali speech. This model can convert Nepali speech to text with a good accuracy of 91% in normal conditions.


- **Developed by:** [Anish Shilpakar](https://github.com/JuJu2181)
- **Language(s) (NLP):** [Nepali]
- **Finetuned from model [optional]:** [wav2vec2](https://huggingface.co/docs/transformers/model_doc/wav2vec2)

## Uses
- For Nepali speech to text transcription
- Can be used for Nepali voice typing
- Can be integrated with other systems like speech summarizer, translation systems.

## Training Details

### Training Data

<!-- This should link to a Data Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->

[OpenSLR](https://openslr.org/54)

### Training Procedure 

<!-- This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. -->
[Training Notebook](https://colab.research.google.com/github/patrickvonplaten/notebooks/blob/master/Fine_tuning_Wav2Vec2_for_English_ASR.ipynb)



#### Metrics

<!-- These are the evaluation metrics being used, ideally with a description of why. -->
[Character Error Rate](https://huggingface.co/spaces/evaluate-metric/cer)
[Word Error Rate](https://en.wikipedia.org/wiki/Word_error_rate)




