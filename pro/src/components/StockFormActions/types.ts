import { FunctionComponent, SVGProps } from 'react'

export interface StockFormRowAction {
  callback: () => void
  label: string
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  disabled?: boolean
}
