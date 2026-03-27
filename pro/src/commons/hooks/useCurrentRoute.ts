import { useMatches } from 'react-router'

import { assertOrFrontendError } from '../errors/assertOrFrontendError'

export const useCurrentRoute = () => {
  const matches = useMatches()

  const currentRoute = matches[matches.length - 1]
  assertOrFrontendError(currentRoute, '`currentRoute` is undefined.')

  return currentRoute
}
