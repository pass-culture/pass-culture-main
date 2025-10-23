export const SIRET_LENGTH = 14
const RID7_LENGTH = 7
const RIDET_LENGTH = 10
const NEW_CALEDONIA_SIREN_PREFIX = 'NC'
const NEW_CALEDONIA_SIREN_PREFIX_LEN = NEW_CALEDONIA_SIREN_PREFIX.length
export const RIDET_WITH_PREFIX_LENGTH =
  RIDET_LENGTH + NEW_CALEDONIA_SIREN_PREFIX_LEN
const NEW_CALEDONIA_SIRET_PADDING_CHAR = 'X'
const NEW_CALEDONIA_SIREN_PADDING_CHAR_LEN =
  SIRET_LENGTH - NEW_CALEDONIA_SIREN_PREFIX_LEN - RIDET_LENGTH

import { removeWhitespaces } from '@/commons/utils/string'

export const unhumanizeSiret = (siret: string) =>
  removeWhitespaces(siret.replace(/\D/g, ''))

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

export const validSiretLength = (siret: string) =>
  unhumanizeSiret(siret).length === SIRET_LENGTH

export const isSiretStartingWithSiren = (
  siret: string,
  siren?: string | null
) =>
  siren !== null &&
  siren !== undefined &&
  unhumanizeSiret(siret).startsWith(unhumanizeSiret(siren))

// RIDET
export const unhumanizeRidet = (
  ridet: string,
  withPrefix: boolean = true,
  withPadding: boolean = true
) => {
  const digits = ridet.replace(/\D/g, '')
  const numericPart = digits.slice(0, 10)
  const NEW_CALEDONIA_SIREN_SUFFIX = NEW_CALEDONIA_SIRET_PADDING_CHAR.repeat(
    NEW_CALEDONIA_SIREN_PADDING_CHAR_LEN
  )
  return `${withPrefix ? NEW_CALEDONIA_SIREN_PREFIX : ''}${numericPart}${withPadding && numericPart.length === 10 ? NEW_CALEDONIA_SIREN_SUFFIX : ''}`
}

export const validRidetWithPrefixLength = (ridet: string): boolean => {
  return unhumanizeRidet(ridet, true, false).length === RIDET_WITH_PREFIX_LENGTH
}

export const isRidetStartingWithRid7 = (
  ridet: string,
  rid7?: string | null
) => {
  return (
    rid7 !== null &&
    rid7 !== undefined &&
    unhumanizeRidet(rid7, true).length ===
      RID7_LENGTH + NEW_CALEDONIA_SIREN_PREFIX_LEN &&
    unhumanizeRidet(ridet, true).startsWith(unhumanizeRidet(rid7, true))
  )
}
