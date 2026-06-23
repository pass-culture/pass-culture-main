import type { FunctionComponent, SVGProps } from 'react'

declare module '*.svg' {
  export const ReactComponent: FunctionComponent<
    SVGProps<SVGSVGElement> & { title?: string }
  >

  const src: string
  export default src
}
