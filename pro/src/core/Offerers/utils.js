import { removeWhitespaces } from 'utils/string'

export const unhumanizeSiren = siret =>
  removeWhitespaces(siret.replace(/[^[0-9]/g, ''))

export const humanizeSiren = siret => {
  const normalizedSiren = siret && unhumanizeSiren(siret)

  if (!normalizedSiren) {
    return ''
  }

  const siren = normalizedSiret.substring(0, 9)
  const sirenWithThreeBatchesOfThreeNumbers = (
    siren.match(/.{1,3}/g) || []
  ).join(' ')
  return sirenWithThreeBatchesOfThreeNumbers.trim()
}
