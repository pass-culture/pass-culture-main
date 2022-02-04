import { removeWhitespaces } from 'react-final-form-utils'

export const formatSiret = string => {
  const value = removeWhitespaces(string)

  if (!value) {
    return ''
  }

  if (isNaN(value)) {
    return string.slice(0, -1)
  }

  const siren = value.substring(0, 9)
  const nic = value.substring(9)
  const sirenWithThreeBatchesOfThreeNumbers = (
    siren.match(/.{1,3}/g) || []
  ).join(' ')
  return `${sirenWithThreeBatchesOfThreeNumbers} ${nic}`.trim()
}
