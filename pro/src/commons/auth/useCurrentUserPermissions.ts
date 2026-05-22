import { useMemo } from 'react'

import { useAppSelector } from '../hooks/useAppSelector'
import { getCurrentUserPermissions } from './getCurrentUserPermissions'
import type { UserPermissions } from './types'

export const useCurrentUserPermissions = (): UserPermissions => {
  const user = useAppSelector((state) => state.user)

  return useMemo(() => getCurrentUserPermissions(user), [user])
}
