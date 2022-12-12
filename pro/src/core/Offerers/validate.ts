export const validateSiren = (siren: string): string => {
  if (siren.length !== 9) {
    return 'Le SIREN doit comporter 9 caractères.'
  }
  return ''
}
