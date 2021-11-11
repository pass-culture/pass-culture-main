import { removeWhitespaces } from 'react-final-form-utils'

const formatSiren = input => {
  if (!input) return ''

  const inputWithoutWhitespaces = removeWhitespaces(input)
  const siren = inputWithoutWhitespaces.substring(0, 9)
  const sirenWithOnlyDigits = siren.replace(/[/\D]/, '')

  return sirenWithOnlyDigits
}

export default formatSiren
