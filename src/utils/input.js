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

export function sanitizeCoordinates(input) {
  const result = parseFloat(
    String(input)
      .replace(',', '.')
      .replace(/[^0-9.]/g, '')
  )
  if (isNaN(result)) {
    return 0.0
  }

  return result
}
