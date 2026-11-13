import { createPath, resolvePath } from 'react-router'

export const getInternalRedirectUrl = (
  redirectTo: string,
  search?: ConstructorParameters<typeof URLSearchParams>[0]
): string => {
  // Ensure to have a new path that "navigate" can go to (even a non-existing one)
  const path = resolvePath(redirectTo)
  const redirectSearchParams = new URLSearchParams(path.search)
  if (search) {
    for (const [key, value] of new URLSearchParams(search)) {
      redirectSearchParams.set(key, value)
    }
  }
  path.search =
    redirectSearchParams.size > 0 ? `?${redirectSearchParams.toString()}` : ''
  return createPath(path)
}
