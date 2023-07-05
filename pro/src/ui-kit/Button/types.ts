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
  icon?: string
  variant?: ButtonVariant
  iconPosition?: IconPositionEnum
  testId?: string
}
