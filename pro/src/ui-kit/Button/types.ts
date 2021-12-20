import { FunctionComponent, SVGProps } from 'react'

export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERNARY = 'ternary',
}

export type SharedButtonProps = {
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  variant?: ButtonVariant
}
