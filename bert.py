
# !/usr/bin/env/python3
# Copyright (c) Facebook, Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""AG news Classification script."""

import os
from argparse import ArgumentParser
import pandas as pd
import pytorch_lightning as pl
import requests
import torch
import torch.nn.functional as F
from pytorch_lightning import seed_everything
from pytorch_lightning.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    LearningRateMonitor,
)
from pytorch_lightning.metrics import Accuracy
from sklearn.model_selection import (
    train_test_split,
)
from torch import nn
from torch.utils.data import Dataset, DataLoader
import torchtext.datasets as td
from transformers import (
    BertModel,
    BertTokenizer,
    AdamW,
)


class AGNewsDataset(Dataset):
    def __init__(
        self,
        reviews,
        targets,
        tokenizer,
        max_length,
    ):
        """
        Performs initialization of tokenizer

        :param reviews: AG news text
        :param targets: labels
        :param tokenizer: bert tokenizer
        :param max_length: maximum length of the news text

        """
        self.reviews = reviews
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        """
        :return: returns the number of datapoints in the dataframe

        """
        return len(self.reviews)

    def __getitem__(self, item):
        """
        Returns the review text and the targets of the specified item

        :param item: Index of sample review

        :return: Returns the dictionary of review text, input ids, attention mask, targets
        """
        review = str(self.reviews[item])
        target = self.targets[item]

        encoding = self.tokenizer.encode_plus(
            review,
            add_special_tokens=True,
            max_length=self.max_length,
            return_token_type_ids=False,
            padding="max_length",
            return_attention_mask=True,
            return_tensors="pt",
            truncation=True,
        )

        return {
            "review_text": review,
            "input_ids": encoding[
                "input_ids"
            ].flatten(),
            "attention_mask": encoding[
                "attention_mask"
            ].flatten(),
            "targets": torch.tensor(
                target, dtype=torch.long
            ),
        }


class BertDataModule(pl.LightningDataModule):
    def __init__(self, **kwargs):
        """
        Initialization of inherited lightning data module
        """
        super(BertDataModule, self).__init__()
        self.PRE_TRAINED_MODEL_NAME = (
            "bert-base-uncased"
        )
        self.df_train = None
        self.df_val = None
        self.df_test = None
        self.train_data_loader = None
        self.val_data_loader = None
# !/usr/bin/env/python3
# Copyright (c) Facebook, Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""AG news Classification script."""

import os
from argparse import ArgumentParser
import pandas as pd
import pytorch_lightning as pl
import requests
import torch
import torch.nn.functional as F
from pytorch_lightning import seed_everything
from pytorch_lightning.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    LearningRateMonitor,
)
from pytorch_lightning.metrics import Accuracy
from sklearn.model_selection import (
    train_test_split,
)
from torch import nn
from torch.utils.data import Dataset, DataLoader
import torchtext.datasets as td
from transformers import (
    BertModel,
    BertTokenizer,
    AdamW,
)


class AGNewsDataset(Dataset):
    def __init__(
        self,
        reviews,
        targets,
        tokenizer,
        max_length,
    ):
        """
        Performs initialization of tokenizer

        :param reviews: AG news text
        :param targets: labels
        :param tokenizer: bert tokenizer
        :param max_length: maximum length of the news text

        """
        self.reviews = reviews
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        """
        :return: returns the number of datapoints in the dataframe

        """
        return len(self.reviews)

    def __getitem__(self, item):
        """
        Returns the review text and the targets of the specified item

        :param item: Index of sample review

        :return: Returns the dictionary of review text, input ids, attention mask, targets
        """
        review = str(self.reviews[item])
        target = self.targets[item]

        encoding = self.tokenizer.encode_plus(
            review,
            add_special_tokens=True,
            max_length=self.max_length,
            return_token_type_ids=False,
            padding="max_length",
            return_attention_mask=True,
            return_tensors="pt",
            truncation=True,
        )

        return {
            "review_text": review,
            "input_ids": encoding[
                "input_ids"
            ].flatten(),
            "attention_mask": encoding[
                "attention_mask"
            ].flatten(),
            "targets": torch.tensor(
                target, dtype=torch.long
            ),
        }


class BertDataModule(pl.LightningDataModule):
    def __init__(self, **kwargs):
        """
        Initialization of inherited lightning data module
        """
        super(BertDataModule, self).__init__()
        self.PRE_TRAINED_MODEL_NAME = (
            "bert-base-uncased"
        )
        self.df_train = None
        self.df_val = None
        self.df_test = None
        self.train_data_loader = None
        self.val_data_loader = None
        self.test_data_loader = None
        self.MAX_LEN = 100
        self.encoding = None
        self.tokenizer = None
        self.args = kwargs
        self.NUM_SAMPLES_COUNT = self.args[
            "num_samples"
        ]
        self.VOCAB_FILE_URL = self.args[
            "vocab_file"
        ]
        self.VOCAB_FILE = (
            "bert_base_uncased_vocab.txt"
        )

    @staticmethod
    def process_label(rating):
        rating = int(rating)
        return rating - 1

    def prepare_data(self):
        """
        Implementation of abstract class
        """

    def setup(self, stage=None):
        """
        Downloads the data, parse it and split the data into train, test, validation data

        :param stage: Stage - training or testing
        """
        # reading  the input
        td.AG_NEWS(
            root="data", split=("train", "test")
        )
        extracted_files = os.listdir("data")

        train_csv_path = None
        for fname in extracted_files:
            if fname.endswith("train.csv"):
                train_csv_path = os.path.join(
                    os.getcwd(), "data", fname
                )
        df = pd.read_csv(train_csv_path)

        df.columns = [
            "label",
            "title",
            "description",
        ]
        df.sample(frac=1)
        df = df.iloc[: self.NUM_SAMPLES_COUNT]

        df["label"] = df.label.apply(
            self.process_label
        )

        if not os.path.isfile(self.VOCAB_FILE):
            filePointer = requests.get(
                self.VOCAB_FILE_URL,
                allow_redirects=True,
            )
            if filePointer.ok:
                with open(
                    self.VOCAB_FILE, "wb"
                ) as f:
                    f.write(filePointer.content)
            else:
                raise RuntimeError(
                    "Error in fetching the vocab file"
                )

        self.tokenizer = BertTokenizer(
            self.VOCAB_FILE
        )

        RANDOM_SEED = 42
        seed_everything(RANDOM_SEED)

        df_train, df_test = train_test_split(
            df,
            test_size=0.2,
            random_state=RANDOM_SEED,
            stratify=df["label"],
        )
        df_train, df_val = train_test_split(
            df_train,
            test_size=0.25,
            random_state=RANDOM_SEED,
            stratify=df_train["label"],
        )

        self.df_train = df_train
        self.df_test = df_test
        self.df_val = df_val

    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Returns the review text and the targets of the specified item

        :param parent_parser: Application specific parser

        :return: Returns the augmented arugument parser
        """
        parser = ArgumentParser(
            parents=[parent_parser],
            add_help=False,
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=16,
            metavar="N",
            help="input batch size for training (default: 16)",
        )
        parser.add_argument(
            "--num-workers",
            type=int,
            default=3,
            metavar="N",
            help="number of workers (default: 0)",
        )
        return parser

    def create_data_loader(
        self, df, tokenizer, max_len, batch_size
    ):
        """
        Generic data loader function

        :param df: Input dataframe
        :param tokenizer: bert tokenizer
        :param max_len: Max length of the news datapoint
        :param batch_size: Batch size for training

        :return: Returns the constructed dataloader
        """
        ds = AGNewsDataset(
            reviews=df.description.to_numpy(),
            targets=df.label.to_numpy(),
            tokenizer=tokenizer,
            max_length=max_len,
        )

        return DataLoader(
            ds,
            batch_size=self.args["batch_size"],
            num_workers=self.args["num_workers"],
        )

    def train_dataloader(self):
        """
        :return: output - Train data loader for the given input
        """
        self.train_data_loader = self.create_data_loader(
            self.df_train,
            self.tokenizer,
            self.MAX_LEN,
            self.args["batch_size"],
        )
        return self.train_data_loader

    def val_dataloader(self):
        """
        :return: output - Validation data loader for the given input
        """
        self.val_data_loader = self.create_data_loader(
            self.df_val,
            self.tokenizer,
            self.MAX_LEN,
            self.args["batch_size"],
        )
        return self.val_data_loader

    def test_dataloader(self):
        """
        :return: output - Test data loader for the given input
        """
        self.test_data_loader = self.create_data_loader(
            self.df_test,
            self.tokenizer,
            self.MAX_LEN,
            self.args["batch_size"],
        )
        return self.test_data_loader


class BertNewsClassifier(pl.LightningModule):
    def __init__(self, **kwargs):
        """
        Initializes the network, optimizer and scheduler
        """
        super(BertNewsClassifier, self).__init__()

        self.train_acc = Accuracy()
        self.val_acc = Accuracy()
        self.test_acc = Accuracy()

        self.PRE_TRAINED_MODEL_NAME = (
            "bert-base-uncased"
        )
        self.bert_model = BertModel.from_pretrained(
            self.PRE_TRAINED_MODEL_NAME
        )
        for param in self.bert_model.parameters():
            param.requires_grad = False
        self.drop = nn.Dropout(p=0.2)
        # assigning labels
        self.class_names = [
            "world",
            "Sports",
            "Business",
            "Sci/Tech",
        ]
        n_classes = len(self.class_names)

        self.fc1 = nn.Linear(
            self.bert_model.config.hidden_size,
            512,
        )
        self.out = nn.Linear(512, n_classes)

        self.args = kwargs

    def forward(self, input_ids, attention_mask):
        """
        :param input_ids: Input data
        :param attention_maks: Attention mask value

        :return: output - Type of news for the given news snippet
        """
        pooled_output = self.bert_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        ).pooler_output
        output = F.relu(self.fc1(pooled_output))
        output = self.drop(output)
        output = self.out(output)
        return output

    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Returns the review text and the targets of the specified item

        :param parent_parser: Application specific parser

        :return: Returns the augmented arugument parser
        """
        parser = ArgumentParser(
            parents=[parent_parser],
            add_help=False,
        )
        parser.add_argument(
            "--lr",
            type=float,
            default=0.001,
            metavar="LR",
            help="learning rate (default: 0.001)",
        )
        return parser

    def training_step(
        self, train_batch, batch_idx
    ):
        """
        Training the data as batches and returns training loss on each batch

        :param train_batch Batch data
        :param batch_idx: Batch indices

        :return: output - Training loss
        """
        input_ids = train_batch["input_ids"]
        attention_mask = train_batch[
            "attention_mask"
        ]
        targets = train_batch["targets"]
        output = self.forward(
            input_ids, attention_mask
        )
        _, y_hat = torch.max(output, dim=1)
        loss = F.cross_entropy(output, targets)
        self.train_acc(y_hat, targets)
        self.log(
            "train_acc",
            self.train_acc.compute().cpu(),
        )
        self.log("train_loss", loss.cpu())
        return {"loss": loss}

    def test_step(self, test_batch, batch_idx):
        """
        Performs test and computes the accuracy of the model

        :param test_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - Testing accuracy
        """
        input_ids = test_batch["input_ids"]
        attention_mask = test_batch[
            "attention_mask"
        ]
        targets = test_batch["targets"]
        output = self.forward(
            input_ids, attention_mask
        )
        _, y_hat = torch.max(output, dim=1)
        self.test_acc(y_hat, targets)
        self.log(
            "test_acc",
            self.test_acc.compute().cpu(),
        )

    def validation_step(
        self, val_batch, batch_idx
    ):
        """
        Performs validation of data in batches

        :param val_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - valid step loss
        """

        input_ids = val_batch["input_ids"]
        attention_mask = val_batch[
            "attention_mask"
        ]
        targets = val_batch["targets"]
        output = self.forward(
            input_ids, attention_mask
        )
        _, y_hat = torch.max(output, dim=1)
        loss = F.cross_entropy(output, targets)
        self.val_acc(y_hat, targets)
        self.log(
            "val_acc",
            self.val_acc.compute().cpu(),
        )
        self.log("val_loss", loss, sync_dist=True)

    def configure_optimizers(self):
        """
        Initializes the optimizer and learning rate scheduler

        :return: output - Initialized optimizer and scheduler
        """
        optimizer = AdamW(
            self.parameters(), lr=self.args["lr"]
        )
        scheduler = {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode="min",
                factor=0.2,
                patience=2,
                min_lr=1e-6,
                verbose=True,
            ),
            "monitor": "val_loss",
        }
        return [optimizer], [scheduler]


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Bert-News Classifier Example"
    )

    parser.add_argument(
        "--num_samples",
        type=int,
        default=15000,
        metavar="N",
        help="Samples for training and evaluation steps (default: 15000) Maximum:100000",
    )
    parser.add_argument(
        "--vocab_file",
        default="https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased-vocab.txt",
        help="Custom vocab file",
    )
    parser.add_argument(
        "--checkpoint_dir",
        default="/home/user/checkpoint/",
        help="Path of checkpoint directory",
    )
    parser.add_argument(
        "--model_save_path",
        default="/home/user/model",
        help="Path to model file",
    )

    parser = pl.Trainer.add_argparse_args(
        parent_parser=parser
    )
    parser = BertNewsClassifier.add_model_specific_args(
        parent_parser=parser
    )
    parser = BertDataModule.add_model_specific_args(
        parent_parser=parser
    )

    args = parser.parse_args()
    dict_args = vars(args)

    if "accelerator" in dict_args:
        if dict_args["accelerator"] == "None":
            dict_args["accelerator"] = None

    dm = BertDataModule(**dict_args)
    dm.prepare_data()
    dm.setup(stage="fit")

    model = BertNewsClassifier(**dict_args)
    early_stopping = EarlyStopping(
        monitor="val_loss",
        mode="min",
        verbose=True,
    )

    checkpoint_callback = ModelCheckpoint(
        dirpath=dict_args["checkpoint_dir"],
        save_top_k=1,
        verbose=True,
        monitor="val_loss",
        mode="min",
    )
    lr_logger = LearningRateMonitor()

    trainer = pl.Trainer.from_argparse_args(
        # args, callbacks=[lr_logger, early_stopping, checkpoint_callback], checkpoint_callback=True, plugins=DDPPlugin(cluster_environment=KubeflowEnvironment)
        args,
        callbacks=[
            lr_logger,
            early_stopping,
            checkpoint_callback,
        ],
        checkpoint_callback=True,
    )
    trainer.fit(model, dm)
    trainer.test(model)

    if trainer.global_rank == 0:
        os.makedirs(dict_args["model_save_path"])
        torch.save(
            model.state_dict(),
            os.path.join(
                dict_args["model_save_path"],
                "bert.pt",
            ),
        )
 
        self.test_data_loader = None
        self.MAX_LEN = 100
        self.encoding = None
        self.tokenizer = None
        self.args = kwargs
        self.NUM_SAMPLES_COUNT = self.args[
            "num_samples"
        ]
        self.VOCAB_FILE_URL = self.args[
            "vocab_file"
        ]
        self.VOCAB_FILE = (
            "bert_base_uncased_vocab.txt"
        )

    @staticmethod
    def process_label(rating):
        rating = int(rating)
        return rating - 1

    def prepare_data(self):
        """
        Implementation of abstract class
        """

    def setup(self, stage=None):
        """
        Downloads the data, parse it and split the data into train, test, validation data

        :param stage: Stage - training or testing
        """
        # reading  the input
        td.AG_NEWS(
            root="data", split=("train", "test")
        )
        extracted_files = os.listdir("data")

        train_csv_path = None
        for fname in extracted_files:
            if fname.endswith("train.csv"):
                train_csv_path = os.path.join(
                    os.getcwd(), "data", fname
                )
        df = pd.read_csv(train_csv_path)

        df.columns = [
            "label",
            "title",
            "description",
        ]
        df.sample(frac=1)
        df = df.iloc[: self.NUM_SAMPLES_COUNT]

        df["label"] = df.label.apply(
            self.process_label
        )

        if not os.path.isfile(self.VOCAB_FILE):
            filePointer = requests.get(
                self.VOCAB_FILE_URL,
                allow_redirects=True,
            )
            if filePointer.ok:
                with open(
                    self.VOCAB_FILE, "wb"
                ) as f:
                    f.write(filePointer.content)
            else:
                raise RuntimeError(
                    "Error in fetching the vocab file"
                )

        self.tokenizer = BertTokenizer(
            self.VOCAB_FILE
        )

        RANDOM_SEED = 42
        seed_everything(RANDOM_SEED)

        df_train, df_test = train_test_split(
            df,
            test_size=0.2,
            random_state=RANDOM_SEED,
            stratify=df["label"],
        )
        df_train, df_val = train_test_split(
            df_train,
            test_size=0.25,
            random_state=RANDOM_SEED,
            stratify=df_train["label"],
        )

        self.df_train = df_train
        self.df_test = df_test
        self.df_val = df_val

    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Returns the review text and the targets of the specified item

        :param parent_parser: Application specific parser

        :return: Returns the augmented arugument parser
        """
        parser = ArgumentParser(
            parents=[parent_parser],
            add_help=False,
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=16,
            metavar="N",
            help="input batch size for training (default: 16)",
        )
        parser.add_argument(
            "--num-workers",
            type=int,
            default=3,
            metavar="N",
            help="number of workers (default: 0)",
        )
        return parser

    def create_data_loader(
        self, df, tokenizer, max_len, batch_size
    ):
        """
        Generic data loader function

        :param df: Input dataframe
        :param tokenizer: bert tokenizer
        :param max_len: Max length of the news datapoint
        :param batch_size: Batch size for training

        :return: Returns the constructed dataloader
        """
        ds = AGNewsDataset(
            reviews=df.description.to_numpy(),
            targets=df.label.to_numpy(),
            tokenizer=tokenizer,
            max_length=max_len,
        )

        return DataLoader(
            ds,
            batch_size=self.args["batch_size"],
            num_workers=self.args["num_workers"],
        )

    def train_dataloader(self):
        """
        :return: output - Train data loader for the given input
        """
        self.train_data_loader = self.create_data_loader(
            self.df_train,
            self.tokenizer,
            self.MAX_LEN,
            self.args["batch_size"],
        )
        return self.train_data_loader

    def val_dataloader(self):
        """
        :return: output - Validation data loader for the given input
        """
        self.val_data_loader = self.create_data_loader(
            self.df_val,
            self.tokenizer,
            self.MAX_LEN,
            self.args["batch_size"],
        )
        return self.val_data_loader

    def test_dataloader(self):
        """
        :return: output - Test data loader for the given input
        """
        self.test_data_loader = self.create_data_loader(
            self.df_test,
            self.tokenizer,
            self.MAX_LEN,
            self.args["batch_size"],
        )
        return self.test_data_loader


class BertNewsClassifier(pl.LightningModule):
    def __init__(self, **kwargs):
        """
        Initializes the network, optimizer and scheduler
        """
        super(BertNewsClassifier, self).__init__()

        self.train_acc = Accuracy()
        self.val_acc = Accuracy()
        self.test_acc = Accuracy()

        self.PRE_TRAINED_MODEL_NAME = (
            "bert-base-uncased"
        )
        self.bert_model = BertModel.from_pretrained(
            self.PRE_TRAINED_MODEL_NAME
        )
        for param in self.bert_model.parameters():
            param.requires_grad = False
        self.drop = nn.Dropout(p=0.2)
        # assigning labels
        self.class_names = [
            "world",
            "Sports",
            "Business",
            "Sci/Tech",
        ]
        n_classes = len(self.class_names)

        self.fc1 = nn.Linear(
            self.bert_model.config.hidden_size,
            512,
        )
        self.out = nn.Linear(512, n_classes)

        self.args = kwargs

    def forward(self, input_ids, attention_mask):
        """
        :param input_ids: Input data
        :param attention_maks: Attention mask value

        :return: output - Type of news for the given news snippet
        """
        pooled_output = self.bert_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        ).pooler_output
        output = F.relu(self.fc1(pooled_output))
        output = self.drop(output)
        output = self.out(output)
        return output

    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Returns the review text and the targets of the specified item

        :param parent_parser: Application specific parser

        :return: Returns the augmented arugument parser
        """
        parser = ArgumentParser(
            parents=[parent_parser],
            add_help=False,
        )
        parser.add_argument(
            "--lr",
            type=float,
            default=0.001,
            metavar="LR",
            help="learning rate (default: 0.001)",
        )
        return parser

    def training_step(
        self, train_batch, batch_idx
    ):
        """
        Training the data as batches and returns training loss on each batch

        :param train_batch Batch data
        :param batch_idx: Batch indices

        :return: output - Training loss
        """
        input_ids = train_batch["input_ids"]
        attention_mask = train_batch[
            "attention_mask"
        ]
        targets = train_batch["targets"]
        output = self.forward(
            input_ids, attention_mask
        )
        _, y_hat = torch.max(output, dim=1)
        loss = F.cross_entropy(output, targets)
        self.train_acc(y_hat, targets)
        self.log(
            "train_acc",
            self.train_acc.compute().cpu(),
        )
        self.log("train_loss", loss.cpu())
        return {"loss": loss}

    def test_step(self, test_batch, batch_idx):
        """
        Performs test and computes the accuracy of the model

        :param test_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - Testing accuracy
        """
        input_ids = test_batch["input_ids"]
        attention_mask = test_batch[
            "attention_mask"
        ]
        targets = test_batch["targets"]
        output = self.forward(
            input_ids, attention_mask
        )
        _, y_hat = torch.max(output, dim=1)
        self.test_acc(y_hat, targets)
        self.log(
            "test_acc",
            self.test_acc.compute().cpu(),
        )

    def validation_step(
        self, val_batch, batch_idx
    ):
        """
        Performs validation of data in batches

        :param val_batch: Batch data
        :param batch_idx: Batch indices

        :return: output - valid step loss
        """

        input_ids = val_batch["input_ids"]
        attention_mask = val_batch[
            "attention_mask"
        ]
        targets = val_batch["targets"]
        output = self.forward(
            input_ids, attention_mask
        )
        _, y_hat = torch.max(output, dim=1)
        loss = F.cross_entropy(output, targets)
        self.val_acc(y_hat, targets)
        self.log(
            "val_acc",
            self.val_acc.compute().cpu(),
        )
        self.log("val_loss", loss, sync_dist=True)

    def configure_optimizers(self):
        """
        Initializes the optimizer and learning rate scheduler

        :return: output - Initialized optimizer and scheduler
        """
        optimizer = AdamW(
            self.parameters(), lr=self.args["lr"]
        )
        scheduler = {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode="min",
                factor=0.2,
                patience=2,
                min_lr=1e-6,
                verbose=True,
            ),
            "monitor": "val_loss",
        }
        return [optimizer], [scheduler]


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Bert-News Classifier Example"
    )

    parser.add_argument(
        "--num_samples",
        type=int,
        default=15000,
        metavar="N",
        help="Samples for training and evaluation steps (default: 15000) Maximum:100000",
    )
    parser.add_argument(
        "--vocab_file",
        default="https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased-vocab.txt",
        help="Custom vocab file",
    )
    parser.add_argument(
        "--checkpoint_dir",
        default="/home/user/checkpoint/",
        help="Path of checkpoint directory",
    )
    parser.add_argument(
        "--model_save_path",
        default="/home/user/model",
        help="Path to model file",
    )

    parser = pl.Trainer.add_argparse_args(
        parent_parser=parser
    )
    parser = BertNewsClassifier.add_model_specific_args(
        parent_parser=parser
    )
    parser = BertDataModule.add_model_specific_args(
        parent_parser=parser
    )

    args = parser.parse_args()
    dict_args = vars(args)

    if "accelerator" in dict_args:
        if dict_args["accelerator"] == "None":
            dict_args["accelerator"] = None

    dm = BertDataModule(**dict_args)
    dm.prepare_data()
    dm.setup(stage="fit")

    model = BertNewsClassifier(**dict_args)
    early_stopping = EarlyStopping(
        monitor="val_loss",
        mode="min",
        verbose=True,
    )

    checkpoint_callback = ModelCheckpoint(
        dirpath=dict_args["checkpoint_dir"],
        save_top_k=1,
        verbose=True,
        monitor="val_loss",
        mode="min",
    )
    lr_logger = LearningRateMonitor()

    trainer = pl.Trainer.from_argparse_args(
        # args, callbacks=[lr_logger, early_stopping, checkpoint_callback], checkpoint_callback=True, plugins=DDPPlugin(cluster_environment=KubeflowEnvironment)
        args,
        callbacks=[
            lr_logger,
            early_stopping,
            checkpoint_callback,
        ],
        checkpoint_callback=True,
    )
    trainer.fit(model, dm)
    trainer.test(model)

    if trainer.global_rank == 0:
        os.makedirs(dict_args["model_save_path"])
        torch.save(
            model.state_dict(),
            os.path.join(
                dict_args["model_save_path"],
                "bert.pt",
            ),
        )
