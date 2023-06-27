export const unhumanizeSiren = siren => siren

export const humanizeSiren = value => {
  const siren = value && unhumanizeSiren(value)
  if (!siren) {
    return ''
  }
  const humanSiren = (siren.match(/.{1,3}/g) || []).join(' ')
  return humanSiren.trim()
}
