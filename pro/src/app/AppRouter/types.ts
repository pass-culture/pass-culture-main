import type { IndexRouteObject, NonIndexRouteObject } from 'react-router'

export interface CustomRouteHandle {
  isErrorPage?: boolean
  /**
   * Both:
   * - the Meta Title (`<title>`)
   * - the hidden Accessibility Title read by screen readers (see `usePageTitle`)
   */
  title: string
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
  // TODO (igabriele, 2026-04-29): Make `handle` required once all the `title` props have been moved into `handle`.
  handle?: CustomRouteHandle
  loader: NonIndexRouteObject['loader']
  /** @deprecated Move `title` within `handle` prop: `handle: { title: '...' }`. */
  title?: string
}

export interface CustomRouteGroup extends CustomRouteBase {
  loader: NonIndexRouteObject['loader']
  children: (CustomRouteGroupChild | IndexRouteObject)[]
}
export interface CustomRouteGroupChild extends CustomRouteBase {
  // TODO (igabriele, 2026-04-29): Make `handle` required once all the `title` props have been moved into `handle`.
  handle?: CustomRouteHandle
  /** @deprecated Move `title` within `handle` prop: `handle: { title: '...' }`. */
  title?: string
  loader?: NonIndexRouteObject['loader']
}

export interface RedirectionRouteObject extends NonIndexRouteObject {
  path: string
  featureName?: string
}
