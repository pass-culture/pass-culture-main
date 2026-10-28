import { createPath, resolvePath } from 'react-router'

export const getInternalRedirectUrl = (
  redirectTo: string | null,
  defaultRedirectUrl = '/accueil'
): string => {
  // Ensure to have a new path that "navigate" can go to (even a non-existing one)
  return createPath(resolvePath(redirectTo ?? defaultRedirectUrl))
}
