import type { NonIndexRouteObject } from 'react-router'

interface CustomRouteMeta {
  public?: boolean
}

export interface CustomRouteObject extends NonIndexRouteObject {
  path: string
  title: string
  element?: JSX.Element
  meta?: CustomRouteMeta
  featureName?: string
  children?: CustomRouteObject[]
  isErrorPage?: boolean
}

export interface RedirectionRouteObject extends NonIndexRouteObject {
  path: string
  featureName?: string
}
