from unittest.mock import MagicMock, patch
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.dashboard.utils import file_helpers


@patch("foliotrack.dashboard.utils.file_helpers.PORTFOLIOS_DIR")
def test_get_portfolio_files(mock_dir):
    mock_dir.exists.return_value = True
    # mock glob to yield fake files
    mock_file_1 = MagicMock()
    mock_file_1.name = "fake1.json"
    mock_file_2 = MagicMock()
    mock_file_2.name = "fake2.json"

    mock_dir.glob.return_value = [mock_file_1, mock_file_2]

    files = file_helpers.get_portfolio_files()
    assert len(files) == 2
    assert files[0].name == "fake1.json"


@patch("foliotrack.dashboard.utils.file_helpers.PORTFOLIOS_DIR")
def test_get_portfolio_filenames(mock_dir):
    """
    Test extraction of only filenames from a directory of portfolio objects.
    """
    mock_file = MagicMock()
    mock_file.name = "example.json"
    mock_dir.glob.return_value = [mock_file]

    names = file_helpers.get_portfolio_filenames()
    assert len(names) == 1
    assert names[0] == "example.json"


@patch("foliotrack.dashboard.utils.file_helpers.PortfolioRepository")
@patch("foliotrack.dashboard.utils.file_helpers.PORTFOLIOS_DIR")
def test_load_portfolio(mock_dir, mock_repo_class):
    """
    Test the loading of a portfolio via the foliotrack PortfolioRepository mapping.
    Ensures the mocked filepath properly routes to load_from_json.
    """
    mock_repo_instance = mock_repo_class.return_value
    mock_portfolio = MagicMock(spec=Portfolio)
    mock_repo_instance.load_from_json.return_value = mock_portfolio
    mock_dir.__truediv__.return_value = "fake/path.json"

    p = file_helpers.load_portfolio("fake.json")

    assert p == mock_portfolio
    mock_repo_instance.load_from_json.assert_called_once_with("fake/path.json")


@patch("foliotrack.dashboard.utils.file_helpers.PortfolioRepository")
@patch("foliotrack.dashboard.utils.file_helpers.PORTFOLIOS_DIR")
def test_save_portfolio(mock_dir, mock_repo_class):
    """
    Test portfolio persistence execution. Verifies if JSON serializer
    is activated faithfully from Portfolios output directory parsing.
    """
    mock_repo_instance = mock_repo_class.return_value
    mock_portfolio = MagicMock(spec=Portfolio)
    mock_dir.__truediv__.return_value = "fake/output.json"

    res = file_helpers.save_portfolio(mock_portfolio, "output.json")

    assert res == "fake/output.json"
    mock_repo_instance.save_to_json.assert_called_once_with(
        mock_portfolio, "fake/output.json"
    )
