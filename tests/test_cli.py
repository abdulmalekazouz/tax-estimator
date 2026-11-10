import json

from taxestimator.cli import main


def test_estimate_text_output(capsys):
    exit_code = main(
        ["estimate", "--year", "2024", "--status", "single", "--wages", "85000"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tax Estimate" in captured.out
    assert "Total tax" in captured.out


def test_estimate_json_output(capsys):
    exit_code = main(
        [
            "estimate",
            "--year",
            "2024",
            "--status",
            "single",
            "--wages",
            "85000",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["tax_year"] == 2024
    assert data["total_tax"] == "10541.00"


def test_compare_across_years(capsys):
    exit_code = main(
        [
            "compare",
            "--years",
            "2023",
            "2024",
            "--status",
            "single",
            "--wages",
            "85000",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert len(data) == 2
    assert {row["tax_year"] for row in data} == {2023, 2024}


def test_report_from_file(tmp_path, capsys):
    input_path = tmp_path / "profiles.json"
    input_path.write_text(
        json.dumps(
            [{"tax_year": 2024, "filing_status": "single", "wages": "60000"}]
        ),
        encoding="utf-8",
    )
    exit_code = main(["report", "--input", str(input_path), "--format", "json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert len(data) == 1
    assert data[0]["filing_status"] == "single"


def test_invalid_number_exits_with_error():
    try:
        main(["estimate", "--year", "2024", "--status", "single", "--wages", "not-a-number"])
        assert False, "expected SystemExit"
    except SystemExit as exc:
        assert exc.code != 0
