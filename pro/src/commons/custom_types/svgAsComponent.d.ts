declare module '*.svg' {
  import * as React from 'react'

  export const ReactComponent: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & { title?: string }
  >

  const src: string
  // biome-ignore lint/style/noDefaultExport: This is a TD file.
  export default src
}
