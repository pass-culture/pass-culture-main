export const validateSiren = (siren: string): string => {
  if (siren.length < 9) {
    return 'SIREN trop court'
  } else if (siren.length > 9) {
    return 'SIREN trop long'
  }
  return ''
}
