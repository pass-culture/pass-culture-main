import { removeWhitespaces } from 'utils/string'

export const formatSirenOrSiret = (sirenOrSiret: string) => {
  const value = removeWhitespaces(sirenOrSiret)
  if (!value) {
    return ''
  }

  if (isNaN(parseInt(value))) {
    return sirenOrSiret.slice(0, -1)
  }

  const siren = value.substring(0, 9)
  const nic = value.substring(9)
  const sirenWithThreeBatchesOfThreeNumbers = (
    siren.match(/.{1,3}/g) || []
  ).join(' ')
  return `${sirenWithThreeBatchesOfThreeNumbers} ${nic}`.trim()
}
