import { useMatches } from 'react-router'

import { assertOrFrontendError } from '../errors/assertOrFrontendError'

export const useCurrentRoute = () => {
  const matches = useMatches()

  const currentRoute = matches.findLast(Boolean)
  assertOrFrontendError(currentRoute, '`currentRoute` is undefined.')

  return currentRoute
}
