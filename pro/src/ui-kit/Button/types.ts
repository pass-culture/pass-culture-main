import { FunctionComponent, SVGProps } from 'react'

export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERNARY = 'ternary',
  QUATERNARY = 'quaternary',
  BOX = 'box',
}

export enum IconPositionEnum {
  RIGHT = 'right',
  LEFT = 'left',
  CENTER = 'center',
}

export type SharedButtonProps = {
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  variant?: ButtonVariant
  iconPosition?: IconPositionEnum
  testId?: string
}
