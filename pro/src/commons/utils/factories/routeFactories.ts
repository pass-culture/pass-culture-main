import type { UIMatch } from 'react-router'

import type { CustomRouteHandle } from '@/app/AppRouter/types'

export const makeCurrentRoute = (
  pathname: string
): UIMatch<unknown, CustomRouteHandle | undefined> => ({
  data: undefined,
  loaderData: undefined,
  handle: undefined,
  id: '0',
  params: {},
  pathname,
})
