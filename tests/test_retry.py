from unittest.mock import patch

import pytest

from src.utils.retry import retry_on_failure


class TestRetryOnFailure:
    def test_succeeds_first_try(self):
        @retry_on_failure(max_retries=3)
        def success():
            return "ok"

        assert success() == "ok"

    @patch('src.utils.retry.time.sleep')
    def test_succeeds_after_retry(self, mock_sleep):
        call_count = 0

        @retry_on_failure(max_retries=3, base_delay=1.0)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        assert flaky() == "ok"
        assert call_count == 3
        assert mock_sleep.call_count == 2

    @patch('src.utils.retry.time.sleep')
    def test_exponential_backoff_delays(self, mock_sleep):
        @retry_on_failure(max_retries=3, base_delay=1.0)
        def always_fail():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fail()

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1.0, 2.0]

    @patch('src.utils.retry.time.sleep')
    def test_raises_after_max_retries(self, mock_sleep):
        @retry_on_failure(max_retries=2, exceptions=(RuntimeError,))
        def always_fail():
            raise RuntimeError("persistent failure")

        with pytest.raises(RuntimeError, match="persistent failure"):
            always_fail()

    def test_does_not_catch_unspecified_exceptions(self):
        @retry_on_failure(max_retries=3, exceptions=(ValueError,))
        def wrong_exception():
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            wrong_exception()
