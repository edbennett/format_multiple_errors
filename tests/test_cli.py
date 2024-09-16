#!/usr/bin/env python3

import pytest

from format_multiple_errors.__main__ import cli

from test_pandas import fixture_dataframe  # noqa: F401


@pytest.fixture(name="df_file")
def fixture_dataframe_file(tmpdir_factory, df):
    filename = tmpdir_factory.mktemp("data").join("testdata.csv")
    df.to_csv(filename, index=False)
    return filename


@pytest.mark.parametrize(
    "params,expected",
    [
        (["--abbreviate"], "3.141(59)(+26/-535)\n"),
        (["--latex"], "3.141 \\pm 0.059 {}^{+0.026}_{-0.535}\n"),
        (["--length_control", "central", "--abbreviate"], "3.1(1)(+0/-5)\n"),
        (["--significant_figures", "1", "--abbreviate"], "3.14(6)(+3/-54)\n"),
    ],
)
def test_cli_number(capsys, params, expected):
    number = ["3.141", "0.059", "0.026,0.535"]
    cli([*params, "format", *number])

    output = capsys.readouterr()
    assert output.out == expected


def test_cli_number_exponential(capsys):
    number = ["31.41", "0.59", "0.26,5.35"]
    cli(["--exponential", "--latex", "format", *number])

    output = capsys.readouterr()
    assert output.out == "(3.141 \\pm 0.059 {}^{+0.026}_{-0.535}) \\times 10^{1}\n"


@pytest.fixture(name="output_text")
def fixture_output_text():
    return (
        "\\begin{tabular}{rrll}\n"
        "\\toprule\n"
        "$a$ & $b$ & $c$ & $d$ \\\\\n"
        "\\midrule\n"
        "3 & 1 & $4.16(26)$ & $3.59({}^{79}_{24})(46)$ \\\\\n"
        "2 & 7 & $1.83(18)$ & $8.459({}^{45}_{235})(360)$ \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
    )


def test_cli_table_stdout(capsys, df_file, output_text):
    cli(
        [
            "--abbreviate",
            "table",
            str(df_file),
            "a",
            "b",
            "c_value,c_error",
            "d_value,d_upper-d_lower,d_systematic",
            "--headings",
            "$a$",
            "$b$",
            "$c$",
            "$d$",
        ]
    )
    output = capsys.readouterr()
    assert output.out == output_text


def test_cli_table_file(df_file, tmp_path, output_text):
    output_path = tmp_path / "output"
    output_path.mkdir()
    output_filename = output_path / "test_output.csv"
    cli(
        [
            "--abbreviate",
            "table",
            str(df_file),
            "a",
            "b",
            "c_value,c_error",
            "d_value,d_upper-d_lower,d_systematic",
            "--headings",
            "$a$",
            "$b$",
            "$c$",
            "$d$",
            "--output_file",
            str(output_filename),
        ]
    )
    with open(output_filename, "r") as f:
        assert f.read() == output_text
