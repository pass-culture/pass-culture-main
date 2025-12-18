import type { NonIndexRouteObject } from 'react-router'

import type { UserPermissions } from '@/commons/auth/types'

/** @deprecated Replaced by `CustomRouteObject.requiredPermissions`. */
interface CustomRouteMeta {
  public?: boolean
  canBeLoggedIn?: boolean
  unattachedOnly?: boolean
  canBeUnattached?: boolean
  onboardingOnly?: boolean
  canBeOnboarding?: boolean
}

export interface CustomRouteObject extends NonIndexRouteObject {
  path: string
  title: string
  element?: JSX.Element
  /** @deprecated Replaced by `CustomRouteObject.requiredPermissions`. */
  meta?: CustomRouteMeta
  featureName?: string
  children?: CustomRouteObject[]
  isErrorPage?: boolean
  requiredPermissions: (userPermissions: UserPermissions) => boolean
}

export interface RedirectionRouteObject extends NonIndexRouteObject {
  path: string
  featureName?: string
}
