import type { NonIndexRouteObject } from 'react-router'

/** @deprecated Replaced by `loader: withUserPermissions(...)`. */
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
  loader: NonIndexRouteObject['loader']
  element?: JSX.Element
  /** @deprecated Replaced by `loader: withUserPermissions(...)`. */
  meta?: CustomRouteMeta
  featureName?: string
  children?: CustomRouteObject[]
  isErrorPage?: boolean
}

export interface RedirectionRouteObject extends NonIndexRouteObject {
  path: string
  featureName?: string
}
