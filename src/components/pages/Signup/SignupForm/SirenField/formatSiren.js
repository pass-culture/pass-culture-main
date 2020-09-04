import { removeWhitespaces } from 'react-final-form-utils'

const formatSiren = input => {
  if (!input) return ''

  const inputWithoutWhitespaces = removeWhitespaces(input)
  const siren = inputWithoutWhitespaces.substring(0, 9)
  const sirenWithOnlyDigits = siren.replace(/[/\D]/, '')

  if (sirenWithOnlyDigits === '') {
    return ''
  }

  const groupThreeNumbersRegex = /.{1,3}/g
  return sirenWithOnlyDigits.match(groupThreeNumbersRegex).join(' ')
}

export default formatSiren
