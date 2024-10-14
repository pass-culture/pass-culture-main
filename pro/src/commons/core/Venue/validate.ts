export const validateSiret = (siret: string): string => {
  if (siret.length < 14) {
    return 'SIRET trop court'
  } else if (siret.length > 14) {
    return 'SIRET trop long'
  }
  return ''
}
