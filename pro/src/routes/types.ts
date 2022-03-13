import type { RouteProps } from 'react-router'

interface ILayoutConfig {
  fullscreen?: boolean
  pageName?: string
}

interface IRouteDataMeta {
  layoutConfig?: ILayoutConfig
  public?: boolean
}

export interface IRouteData extends RouteProps {
  component: React.ComponentType
  featureName?: string
  meta?: IRouteDataMeta
  title: string
}
