import argparse
import toml
from src.dataset import AudioToTextDataLayer
from src.helpers import (
    process_evaluation_batch,
    process_evaluation_epoch,
    add_ctc_labels,
    AmpOptimizations,
    print_dict,
    __ctc_decoder_predictions_tensor,
)
from src.model import AudioPreprocessing, GreedyCTCDecoder, JasperEncoderDecoder
from src.parts.features import audio_from_file
import torch
import random
import numpy as np
import time


def parse_args():
    parser = argparse.ArgumentParser(description="Jasper")
    parser.add_argument("--wav", type=str, required=True)
    parser.add_argument(
        "--model_toml",
        type=str,
        help="relative model configuration path given dataset folder",
    )
    parser.add_argument(
        "--ckpt", default=None, type=str, required=True, help="path to model checkpoint"
    )
    return parser.parse_args()


def run_once(audio_processor, encoderdecoder, greedy_decoder, audio, audio_len, labels):
    features = audio_processor(audio, audio_len)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    t_log_probs_e = encoderdecoder(features[0])
    torch.cuda.synchronize()
    t1 = time.perf_counter()
    t_predictions_e = greedy_decoder(log_probs=t_log_probs_e)
    hypotheses = __ctc_decoder_predictions_tensor(t_predictions_e, labels=labels)
    print("INFERENCE TIME\t\t: {} ms".format((t1 - t0) * 1000.0))
    print("TRANSCRIPT\t\t:", hypotheses[0])


def inference(wav, model, model_toml, seed=42, cudnn_benchmark=False):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.benchmark = cudnn_benchmark
    print("CUDNN BENCHMARK ", cudnn_benchmark)

    optim_level = 0

    jasper_model_definition = toml.load(model_toml)
    dataset_vocab = jasper_model_definition["labels"]["labels"]
    ctc_vocab = add_ctc_labels(dataset_vocab)

    featurizer_config = jasper_model_definition["input_eval"]
    featurizer_config["optimization_level"] = optim_level
    use_conv_mask = jasper_model_definition["encoder"].get("convmask", True)

    print("=== model_config ===")
    print_dict(jasper_model_definition)
    print("=== feature_config ===")
    print_dict(featurizer_config)
    data_layer = None

    audio_preprocessor = AudioPreprocessing(**featurizer_config)
    encoderdecoder = JasperEncoderDecoder(
        jasper_model_definition=jasper_model_definition,
        feat_in=1024,
        num_classes=len(ctc_vocab),
    )

    print("loading model from ", model)
    checkpoint = torch.load(model, map_location="cpu")
    for k in audio_preprocessor.state_dict().keys():
        checkpoint["state_dict"][k] = checkpoint["state_dict"].pop(
            "audio_preprocessor." + k
        )
    audio_preprocessor.load_state_dict(checkpoint["state_dict"], strict=False)
    encoderdecoder.load_state_dict(checkpoint["state_dict"], strict=False)

    greedy_decoder = GreedyCTCDecoder()

    print("audio_preprocessor.normalize: ", audio_preprocessor.featurizer.normalize)

    audio_preprocessor.eval()
    encoderdecoder.eval()
    greedy_decoder.eval()

    audio, audio_len = audio_from_file(wav)

    run_once(audio_processor, encoderdecoder, greedy_decoder, audio, audio_len, ctc_vocab)


if __name__ == "__main__":
    args = parse_args()

    print_dict(vars(args))
    inference(
        "example1.wav",
        "../models/Jasper_1612265229.5877585-epoch-179.pt",
        "../configs/jasper10x5dr_sp_offline_specaugment.toml",
        seed=42,
    )
