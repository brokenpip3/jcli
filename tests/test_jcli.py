from click.testing import CliRunner
import mock
from jcli.cli import jobs, run, config, version, job_exist, main
from jcli.version import __version__

runner = CliRunner()

def test_run_no_name():
    result = runner.invoke(jobs, ["run"])
    assert result.exit_code == 2
    assert "Error: Missing argument 'NAME'." in result.output

def test_run_wrong_name():
    result = runner.invoke(jobs, ["run", "foobar"])
    assert result.exception

def test_get_version():
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert f'version {__version__}' in result.output

@mock.patch('jcli.config.os.path.exists')
def test_config(mock_exist):
    result = runner.invoke(config, input='http://foobar.local\nfoo\nbar\n')
    mock_exist.return_value = [True]
    assert result.exit_code == 1
    assert "Config dir already exist, check the configuration manually" in result.output
