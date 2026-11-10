import type { IndexRouteObject, NonIndexRouteObject } from 'react-router'

export interface CustomRouteHandle {
  isErrorPage?: boolean
  /**
   * Both:
   * - the Meta Title (`<title>`)
   * - the hidden Accessibility Title read by screen readers (see `usePageTitle`)
   */
  title: string
  mainTitle?: string
}

interface CustomRouteBase extends NonIndexRouteObject {
  path: string
  /** FF necessary to access the route */
  featureName?: string
  /** FF that disables the route */
  disabledWithFeatureName?: string
}

export type CustomRouteTree = Array<CustomRouteGroup | CustomRouteOrphan>

export interface CustomRouteOrphan extends CustomRouteBase {
  handle: CustomRouteHandle
  loader: NonIndexRouteObject['loader']
}

export interface CustomRouteGroup extends CustomNestedRouteGroup {
  loader: NonIndexRouteObject['loader']
}
export interface CustomRouteGroupChild extends CustomRouteBase {
  handle: CustomRouteHandle
  loader?: NonNullable<NonIndexRouteObject['loader']>
}

interface CustomNestedRouteGroup extends CustomRouteBase {
  handle?: CustomRouteHandle
  children: (
    | CustomNestedRouteGroup
    | CustomRouteGroupChild
    | IndexRouteObject
  )[]
}

export interface CustomRouteGroupChild extends CustomRouteBase {
  handle: CustomRouteHandle
  loader?: NonNullable<NonIndexRouteObject['loader']>
  children?: never
}

export interface RedirectionRouteObject extends NonIndexRouteObject {
  path: string
  featureName?: string
}
