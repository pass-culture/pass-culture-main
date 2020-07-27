export const shouldApplyTertiaryColor = pathname => {
  const pathWithTertiaryColor = [
    '/accueil',
  ]

  return RegExp(`(${pathWithTertiaryColor.join('|')})$`).test(pathname)
}
