export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERNARY = 'ternary',
  TERNARYPINK = 'ternary-pink',
  QUATERNARY = 'quaternary',
  QUATERNARYPINK = 'quaternary-pink',
  BOX = 'box',
}

export enum IconPositionEnum {
  RIGHT = 'right',
  LEFT = 'left',
  CENTER = 'center',
}

export type SharedButtonProps = {
  icon?: string | null
  variant?: ButtonVariant
  iconPosition?: IconPositionEnum
  testId?: string
}
