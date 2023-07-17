export const cleanURLParam = (param?: string): string => {
  if (param) {
    return param.replace(/[%$*();+={}:]/g, '')
  }

  return ''
}
