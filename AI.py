import torch.nn as nn
import torch
from transformers import BertModel
import os

HIDDEN_DIM = 1024
OUTPUT_DIM = 3


class BERTNLIModel(nn.Module):
    def __init__(self,
                 bert_model,
                 hidden_dim,
                 output_dim,
                 ):
        super().__init__()
        self.bert = bert_model
        embedding_dim = bert_model.config.to_dict()['hidden_size']
        self.out = nn.Linear(embedding_dim, output_dim)

    def forward(self, sequence, attn_mask, token_type):
        embedded = self.bert(input_ids=sequence, attention_mask=attn_mask, token_type_ids=token_type)[1]
        output = self.out(embedded)
        return output

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
bert_model = BertModel.from_pretrained('bert-base-uncased')
model = BERTNLIModel(bert_model,
                     HIDDEN_DIM,
                     OUTPUT_DIM,
                     ).to(device)
print("TEST")
size = os.path.getsize('./models/bert-nli.pt')
print('Size of file is', size, 'bytes\n\n\n')
model.load_state_dict(torch.load('./models/bert-nli.pt', map_location=torch.device('cpu')))
print("TEST2")
model.eval()


def predict_inference(premise, hypothesis, model, device):
    model.eval()

    premise = '[CLS] ' + premise + ' [SEP]'
    hypothesis = hypothesis + ' [SEP]'

    prem_t = tokenize_bert(premise)
    hypo_t = tokenize_bert(hypothesis)

    # print(len(prem_t), len(hypo_t))

    prem_type = get_sent1_token_type(prem_t)
    hypo_type = get_sent2_token_type(hypo_t)

    # print(len(prem_type), len(hypo_type))

    indexes = prem_t + hypo_t

    indexes = tokenizer.convert_tokens_to_ids(indexes)
    # print(indexes)
    indexes_type = prem_type + hypo_type
    # print(indexes_type)

    attn_mask = get_sent2_token_type(indexes)
    # print(attn_mask)

    # print(len(indexes))
    # print(len(indexes_type))
    # print(len(attn_mask))

    # seq = '[CLS] '+ premise + ' [SEP] '+ hypothesis

    # tokens = tokenizer.tokenize(seq)

    # indexes = tokenizer.convert_tokens_to_ids(tokens)

    indexes = torch.LongTensor(indexes).unsqueeze(0).to(device)
    indexes_type = torch.LongTensor(indexes_type).unsqueeze(0).to(device)
    attn_mask = torch.LongTensor(attn_mask).unsqueeze(0).to(device)

    # print(indexes.size())

    prediction = model(indexes, attn_mask, indexes_type)

    prediction = prediction.argmax(dim=-1).item()

    return LABEL[prediction]


def tokenize_bert(sentence):
    tokens = tokenizer.tokenize(sentence)
    # tokens = tokenizer.encode(tokens, padding=True, truncation=True,max_length=400, add_special_tokens = True)
    return tokens


def get_sent1_token_type(sent):
    try:
        return [0] * len(sent)
    except:
        return []


def get_sent2_token_type(sent):
    try:
        return [1] * len(sent)
    except:
        return []


from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

LABEL = ['entailment', 'contradiction', 'neutral']


#def getPrediction(premise, hypothesis):
premise = 'a man sitting on a green bench.'
hypothesis = 'a woman sitting on a green bench.'
print(predict_inference(premise, hypothesis, model, device))
