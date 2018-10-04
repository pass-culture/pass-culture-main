import { removeWhitespaces } from 'pass-culture-shared'

export function formatSiren(string) {
  const value = removeWhitespaces(string)
  if (!value) {
    return ''
  }
  const siren = value.substring(0, 9)
  const nic = value.substring(9)
  const formattedSiren = (siren.match(/.{1,3}/g) || []).join(' ')
  return `${formattedSiren} ${nic}`.trim()
}
