from pathlib import Path
from typing import Union, Text, Optional, List
import diart.sources as src
import pandas as pd
from diart.inference import RealTimeInference
from diart.blocks import BasePipeline, BasePipelineConfig
from diart.progress import ProgressBar, TQDMProgressBar
from pyannote.core import Annotation
from pyannote.database.util import load_rttm
from pyannote.metrics.diarization import DiarizationErrorRate

from os import path

class Benchmark:
    """
    Run an online speaker diarization pipeline on a set of audio files in batches.
    Write predictions to a given output directory.

    If the reference is given, calculate the average diarization error rate.

    Parameters
    ----------
    speech_path: Text or Path
        Directory with audio files.
    reference_path: Text, Path or None
        Directory with reference RTTM files (same names as audio files).
        If None, performance will not be calculated.
        Defaults to None.
    output_path: Text, Path or None
        Output directory to store predictions in RTTM format.
        If None, predictions will not be written to disk.
        Defaults to None.
    show_progress: bool
        Whether to show progress bars.
        Defaults to True.
    show_report: bool
        Whether to print a performance report to stdout.
        Defaults to True.
    batch_size: int
        Inference batch size.
        If < 2, then it will run in real time.
        If >= 2, then it will pre-calculate segmentation and
        embeddings, running the rest in real time.
        The performance between this two modes does not differ.
        Defaults to 16.
    """
    def __init__(
        self,
        speech_path: Union[Text, Path],
        reference_path: Optional[Union[Text, Path]] = None,
        output_path: Optional[Union[Text, Path]] = None,
        show_progress: bool = True,
        show_report: bool = True,
        batch_size: int = 16,
        hyp_value: float = None,
    ):
        self.speech_path = Path(speech_path).expanduser()
        assert self.speech_path.is_dir(), "Speech path must be a directory"

        # If there's no reference and no output, then benchmark has no output
        msg = "Benchmark expected reference path, output path or both"
        assert reference_path is not None or output_path is not None, msg

        self.reference_path = reference_path
        if reference_path is not None:
            self.reference_path = Path(self.reference_path).expanduser()
            assert self.reference_path.is_dir(), "Reference path must be a directory"

        self.output_path = output_path
        if self.output_path is not None:
            self.output_path = Path(output_path).expanduser()
            self.output_path.mkdir(parents=True, exist_ok=True)

        self.show_progress = show_progress
        self.show_report = show_report
        self.batch_size = batch_size
        self.hyp_value = hyp_value

    def get_file_paths(self) -> List[Path]:
        """Return the path for each file in the benchmark.

        Returns
        -------
        paths: List[Path]
            List of audio file paths.
        """
        return list(self.speech_path.iterdir())

    def run_single(
        self,
        pipeline: BasePipeline,
        filepath: Path,
        progress_bar: ProgressBar,
    ) -> Annotation:
        """Run a given pipeline on a given file.
        Note that this method does NOT reset the
        state of the pipeline before execution.

        Parameters
        ----------
        pipeline: BasePipeline
            Speaker diarization pipeline to run.
        filepath: Path
            Path to the target file.
        progress_bar: diart.progress.ProgressBar
            An object to manage the progress of this run.

        Returns
        -------
        prediction: Annotation
            Pipeline prediction for the given file.
        """
        padding = pipeline.config.get_file_padding(filepath)
        source = src.FileAudioSource(
            filepath,
            pipeline.config.sample_rate,
            padding,
            pipeline.config.optimal_block_size(),
        )
        pipeline.set_timestamp_shift(-padding[0])
        inference = RealTimeInference(
            pipeline,
            source,
            self.batch_size,
            do_profile=False,
            do_plot=False,
            show_progress=self.show_progress,
            progress_bar=progress_bar,
        )

        pred = inference()
        pred.uri = source.uri

        if self.output_path is not None:
            with open(self.output_path / f"{source.uri}.rttm", "a+") as out_file:
                out_file.write(f"tau_active = {self.hyp_value}: \n")
                pred.write_rttm(out_file)
                out_file.write("\n")

        return pred

    def evaluate(self, predictions: List[Annotation]) -> Union[pd.DataFrame, List[Annotation]]:
        """If a reference path was provided,
        compute the diarization error rate of a list of predictions.

        Parameters
        ----------
        predictions: List[Annotation]
            Predictions to evaluate.

        Returns
        -------
        report_or_predictions: Union[pd.DataFrame, List[Annotation]]
            A performance report as a pandas `DataFrame` if a
            reference path was given. Otherwise return the same predictions.
        """
        if self.reference_path is not None:
            metric = DiarizationErrorRate(collar=0, skip_overlap=False)
            progress_bar = TQDMProgressBar("Computing DER", leave=False)
            progress_bar.create(total=len(predictions), unit="file")
            progress_bar.start()
            for hyp in predictions:
                ref = load_rttm(self.reference_path / f"{hyp.uri}.rttm").popitem()[1]
                metric(ref, hyp)
                progress_bar.update()
            progress_bar.close()
            report = metric.report(display=self.show_report)

            existing_file_path = path.join(self.output_path, "report.csv")
            if (path.exists(existing_file_path)):
                report.to_csv(existing_file_path, mode='a', header=False, index=True)
            else:
                report.to_csv(existing_file_path, mode='a', header=True, index=True)

            return report
        return predictions

    def __call__(
        self,
        pipeline_class: type,
        config: BasePipelineConfig,
    ) -> Union[pd.DataFrame, List[Annotation]]:
        """Run a given pipeline on a set of audio files.
        Notice that the internal state of the pipeline is reset before benchmarking.

        Parameters
        ----------
        pipeline_class: class
            Class from the BasePipeline hierarchy.
            A pipeline from this class will be instantiated by each worker.
        config: BasePipelineConfig
            Diarization pipeline configuration.

        Returns
        -------
        performance: pandas.DataFrame or List[Annotation]
            If reference annotations are given, a DataFrame with detailed
            performance on each file as well as average performance.

            If no reference annotations, a list of predictions.
        """
        audio_file_paths = self.get_file_paths()
        pipeline = pipeline_class(config)
        filepath = audio_file_paths[0]

        predictions = []
        # pipeline.reset()
        desc = f"Streaming {filepath.stem}"
        progress = TQDMProgressBar(desc, leave=False, do_close=True)
        predictions.append(self.run_single(pipeline, filepath, progress))

        return self.evaluate(predictions)
