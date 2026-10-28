import { generatePath, type LoaderFunctionArgs, redirect } from 'react-router'

import { getUserDefaultPath } from '../../app/AppRouter/utils/getUserDefaultPath'
import { rootStore } from '../store/store'
import { getCurrentUserPermissions } from './getCurrentUserPermissions'
import type { UserPermissions } from './types'

export const withUserPermissions = (
  requireUserPermissions: (userPermissions: UserPermissions) => boolean,
  loader?: (args: LoaderFunctionArgs) => unknown
) => {
  return (args: LoaderFunctionArgs) => {
    const userPermissions = getCurrentUserPermissions(rootStore.getState().user)
    if (!requireUserPermissions(userPermissions)) {
      const redirectTo = generatePath(args.pattern, args.params)
      const searchParams = redirectTo === '/' ? '' : `?redirectTo=${redirectTo}`
      throw redirect(getUserDefaultPath(searchParams))
    }

    return loader?.(args) ?? null
  }
}
