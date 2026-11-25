import { generatePath, type LoaderFunctionArgs, redirect } from 'react-router'

import { getUserDefaultPath } from '../../app/AppRouter/utils/getUserDefaultPath'
import { rootStore } from '../store/store'
import { VENUE_ID_SEARCH_PARAM } from '../store/user/utils/getInitialPartnerVenueId'
import { getCurrentUserPermissions } from './getCurrentUserPermissions'
import type { UserPermissions } from './types'

export const withUserPermissions = (
  requireUserPermissions: (userPermissions: UserPermissions) => boolean,
  loader?: (args: LoaderFunctionArgs) => unknown
) => {
  return (args: LoaderFunctionArgs) => {
    const userPermissions = getCurrentUserPermissions(rootStore.getState().user)
    if (!requireUserPermissions(userPermissions)) {
      const venueId = args.url.searchParams.get(VENUE_ID_SEARCH_PARAM)
      const redirectTo = generatePath(args.pattern, args.params)
      const nextSearchParams = new URLSearchParams({
        ...(venueId && { [VENUE_ID_SEARCH_PARAM]: venueId }),
        ...(redirectTo !== '/' && { redirectTo }),
      })
      const search =
        nextSearchParams.size > 0 ? `?${nextSearchParams.toString()}` : ''
      throw redirect(getUserDefaultPath(search))
    }

    return loader?.(args) ?? null
  }
}
