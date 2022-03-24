import { removeWhitespaces } from 'utils/string'

export const unhumanizeSiren = siren =>
  removeWhitespaces(siren.replace(/[^[0-9]/g, '')).substring(0, 9)

export const humanizeSiren = value => {
  const siren = value && unhumanizeSiren(value)
  if (!siren) {
    return ''
  }
  const humanSiren = (siren.match(/.{1,3}/g) || []).join(' ')
  return humanSiren.trim()
}
