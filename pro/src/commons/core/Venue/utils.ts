import { removeWhitespaces } from '@/commons/utils/string'

export const unhumanizeSiret = (siret: string) =>
  removeWhitespaces(siret.replace(/[^[0-9]/g, ''))

export const humanizeSiret = (siret: string) => {
  const normalizedSiret = siret && unhumanizeSiret(siret)

  if (!normalizedSiret) {
    return ''
  }

  const siren = normalizedSiret.substring(0, 9)
  const nic = normalizedSiret.substring(9)
  const sirenWithThreeBatchesOfThreeNumbers = (
    siren.match(/.{1,3}/g) || []
  ).join(' ')
  return `${sirenWithThreeBatchesOfThreeNumbers} ${nic}`.trim()
}
