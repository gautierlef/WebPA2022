import torch.nn as nn
import torch
from transformers import BertModel


class BERTNLIModel(nn.Module):
    def __init__(self,
                 bert_model,
                 hidden_dim,
                 output_dim,
                 ):
        super().__init__()

        self.bert = bert_model

        embedding_dim = bert_model.config.to_dict()['hidden_size']

        # self.fc = nn.Linear(embedding_dim, hidden_dim)

        # self.fc2 = nn.Linear(hidden_dim, hidden_dim)

        self.out = nn.Linear(embedding_dim, output_dim)

    def forward(self, sequence, attn_mask, token_type):
        # sequence = [sequence len, batch_size]
        # attention_mask = [seq_len, batch_size]
        # token_type = [seq_len, batch_size]

        embedded = self.bert(input_ids=sequence, attention_mask=attn_mask, token_type_ids=token_type)[1]
        # print('emb ', embedded.size())

        # self.bert() gives tuple which contains hidden outut corresponding to each token.
        # self.bert()[0] = [seq_len, batch_size, emd_dim]

        # embedded = [batch size, emb dim]

        # ff = self.fc(embedded)
        # ff = [batch size, hid dim]

        # ff1 = self.fc2(ff)

        output = self.out(embedded)
        # print('output: ', output.size())
        # output = [batch size, out dim]

        return output


HIDDEN_DIM = 1024
OUTPUT_DIM = 3

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

bert_model = BertModel.from_pretrained('bert-base-uncased')

model = BERTNLIModel(bert_model,
                     HIDDEN_DIM,
                     OUTPUT_DIM,
                     ).to(device)

model.load_state_dict(torch.load('./models/bert-nli.pt', map_location=torch.device('cpu')))
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
LABEL

premise = 'a man sitting on a green bench.'
hypothesis = 'a woman sitting on a green bench.'

predict_inference(premise, hypothesis, model, device)
