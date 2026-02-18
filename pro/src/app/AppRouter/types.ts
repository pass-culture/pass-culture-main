import type { IndexRouteObject, NonIndexRouteObject } from 'react-router'

// TODO (igabriele, 2026-02-04): Delete this interface once `WIP_SWITCH_VENUE` FF is enabled and removed.
/** @deprecated Replaced by `loader: withUserPermissions(...)`. */
interface CustomRouteMeta {
  public?: boolean
  canBeLoggedIn?: boolean
  unattachedOnly?: boolean
  canBeUnattached?: boolean
  onboardingOnly?: boolean
  canBeOnboarding?: boolean
}

export interface CustomRouteHandle {
  isErrorPage?: boolean
  // TODO (igabriele, 2026-02-04): Make `title` required once the new route-based layout is fully implemented.
  title?: string
}

interface CustomRouteBase extends NonIndexRouteObject {
  path: string
  /** @deprecated Replaced by `loader: withUserPermissions(...)`. */
  meta?: CustomRouteMeta
  /** FF necessary to access the route */
  featureName?: string
  /** FF that disables the route */
  disabledWithFeatureName?: string
}

export type CustomRouteTree = Array<CustomRouteGroup | CustomRouteOrphan>

export interface CustomRouteOrphan extends CustomRouteBase {
  loader: NonIndexRouteObject['loader']
  /** @deprecated Move `title` within `handle` prop: `handle: { title: '...' }`. */
  title?: string
}

export interface CustomRouteGroup extends CustomRouteBase {
  loader: NonIndexRouteObject['loader']
  children: (CustomRouteGroupChild | IndexRouteObject)[]
}
export interface CustomRouteGroupChild extends CustomRouteBase {
  handle?: CustomRouteHandle
  /** @deprecated Move `title` within `handle` prop: `handle: { title: '...' }`. */
  title?: string
  loader?: NonIndexRouteObject['loader']
}

export interface RedirectionRouteObject extends NonIndexRouteObject {
  path: string
  featureName?: string
}
