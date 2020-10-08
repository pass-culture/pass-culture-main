from pcapi.domain.bank_account import format_raw_iban_and_bic

class FormatRawIbanAndBicTest:
  def test_return_nothing_if_given_data_is_none(self):
      # given
      raw_data = None

      # when
      result = format_raw_iban_and_bic(raw_data)

      # then
      assert result is None

  def test_return_string_without_spaces(self):
      # given
      raw_data = '  STRING WITH SPACE  '

      # when
      result = format_raw_iban_and_bic(raw_data)

      # then
      assert result == 'STRINGWITHSPACE'

  def test_return_uppercased_string(self):
      # given
      raw_data = 'stringToUppercase'

      # when
      result = format_raw_iban_and_bic(raw_data)

      # then
      assert result == 'STRINGTOUPPERCASE'
