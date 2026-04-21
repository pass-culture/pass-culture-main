import { type LoaderFunctionArgs, redirect } from 'react-router'

import { getUserDefaultPath } from '../../app/AppRouter/utils/getUserDefaultPath'
import { getCurrentUserPermissions } from './getCurrentUserPermissions'
import type { UserPermissions } from './types'

export const withUserPermissions = (
  requireUserPermissions: (userPermissions: UserPermissions) => boolean,
  loader?: (args: LoaderFunctionArgs) => unknown
) => {
  return (args: LoaderFunctionArgs) => {
    const userPermissions = getCurrentUserPermissions()
    if (!requireUserPermissions(userPermissions)) {
      throw redirect(getUserDefaultPath())
    }

    return loader?.(args) ?? null
  }
}
