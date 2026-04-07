import pandas as pd

from analyze_process import audio_to_chunks, rename_result_columns, get_result_file_path


class TestAudioToChunks:
    
    def test_produces_correct_offsets(self, mocker):
        mocker.patch("analyze_process.get_duration", return_value=1500)

        chunks = list(audio_to_chunks("file.wav", chunk_size=600))

        assert chunks == [
            (0, 600, 1500),
            (600, 600, 1500),
            (1200, 600, 1500),
        ]

    def test_exact_duration_match(self, mocker):
        mocker.patch("analyze_process.get_duration", return_value=600)

        chunks = list(audio_to_chunks("file.wav", chunk_size=600))

        assert chunks == [(0, 600, 600)]

    def test_shorter_than_chunk(self, mocker):
        mocker.patch("analyze_process.get_duration", return_value=10)

        chunks = list(audio_to_chunks("file.wav", chunk_size=600))

        assert chunks == [(0, 600, 10)]


class TestRenameResultColumns:

    def test_renames_columns(self):
        df = pd.DataFrame({
            "a": [0.0],
            "b": [3.0],
            "c": ["Species A"],
            "d": ["Common A"],
            "e": [0.95],
        })

        result = rename_result_columns(df)

        assert list(result.columns) == [
            "Start (s)", "End (s)", "Scientific name", "Common name", "Confidence",
        ]

    def test_empty_dataframe(self):
        result = rename_result_columns(pd.DataFrame())

        assert result.empty
        assert list(result.columns) == [
            "Start (s)", "End (s)", "Scientific name", "Common name", "Confidence",
        ]


class TestGetResultFilePath:

    def test_flat_structure(self):
        result = get_result_file_path(
            file_path="/input/recording.wav",
            input_folder_path="/input",
            output_folder_path="/output",
            model_name="MyModel",
        )

        assert result == "/output/recording.MyModel.results.csv"

    def test_nested_structure_is_preserved(self):
        result = get_result_file_path(
            file_path="/input/subdir/deep/recording.mp3",
            input_folder_path="/input",
            output_folder_path="/output",
            model_name="MyModel",
        )

        assert result == "/output/subdir/deep/recording.MyModel.results.csv"


