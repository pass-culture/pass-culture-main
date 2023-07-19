import { removeWhitespaces } from 'utils/string'

export const unhumanizeSiren = (siren: string) =>
  removeWhitespaces(siren.replace(/[^[0-9]/g, '')).substring(0, 9)

export const humanizeSiren = (value: string) => {
  const siren = value && unhumanizeSiren(value)
  if (!siren) {
    return ''
  }
  const humanSiren = (siren.match(/.{1,3}/g) || []).join(' ')
  return humanSiren.trim()
}
