import { removeWhitespaces } from 'commons/utils/string'

export const unhumanizeSiren = (siren: string) =>
  removeWhitespaces(siren.replace(/[^[0-9]/g, '')).substring(0, 9)
