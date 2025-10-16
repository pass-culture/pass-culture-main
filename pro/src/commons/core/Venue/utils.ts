import { removeWhitespaces } from '@/commons/utils/string'

export const unhumanizeSiret = (siret: string) =>
  removeWhitespaces(siret.replace(/[^0-9]/g, ''))

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

export const unhumanizeRidet = (ridet: string) =>
  removeWhitespaces(ridet.toUpperCase().replace(/[^NC0-9]/g, ''))

export const isRidet = (ridet: string): boolean => {
  const unhumanizedRidet = unhumanizeRidet(ridet)
  switch (unhumanizedRidet?.length) {
    case 0:
      return false
    case 1:
      return unhumanizedRidet.startsWith('N')
    case 2:
      return unhumanizedRidet.startsWith('NC')
    default:
      return /^NC[0-9]{0,12}$/.test(unhumanizedRidet)
  }
}

export const humanizeRidet = (ridet: string) => {
  const normalizedRidet = ridet && unhumanizeRidet(ridet)

  if (!normalizedRidet) {
    return ''
  }

  const siren = normalizedRidet.substring(2, 11)
  const sirenWithThreeBatchesOfThreeNumbers = (
    siren.match(/.{1,3}/g) || []
  ).join(' ')
  return `NC${sirenWithThreeBatchesOfThreeNumbers}`.trim()
}
