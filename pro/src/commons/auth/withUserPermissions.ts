import { type LoaderFunctionArgs, redirect } from 'react-router'

import { isFeatureActive } from '@/commons/store/features/selectors'
import { rootStore } from '@/commons/store/store'

import { getUserDefaultPath } from '../../app/AppRouter/utils/getUserDefaultPath'
import { getCurrentUserPermissions } from './getCurrentUserPermissions'
import type { UserPermissions } from './types'

export const withUserPermissions = (
  requireUserPermissions: (userPermissions: UserPermissions) => boolean,
  loader?: (args: LoaderFunctionArgs) => unknown
) => {
  return (args: LoaderFunctionArgs) => {
    const state = rootStore.getState()

    if (!isFeatureActive(state, 'WIP_SWITCH_VENUE')) {
      return loader?.(args) ?? null
    }

    const userPermissions = getCurrentUserPermissions()
    if (!requireUserPermissions(userPermissions)) {
      throw redirect(getUserDefaultPath())
    }

    return loader?.(args) ?? null
  }
}
