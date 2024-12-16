import { type EnumType } from 'commons/custom_types/utils'

export const ButtonVariant = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  TERNARY: 'ternary',
  TERNARYPINK: 'ternary-pink',
  QUATERNARY: 'quaternary',
  QUATERNARYPINK: 'quaternary-pink',
  BOX: 'box',
} as const
// eslint-disable-next-line no-redeclare
export type ButtonVariant = EnumType<typeof ButtonVariant>

export const IconPositionEnum = {
  RIGHT: 'right',
  LEFT: 'left',
  CENTER: 'center',
} as const
// eslint-disable-next-line no-redeclare
export type IconPositionEnum = EnumType<typeof IconPositionEnum>

export type SharedButtonProps = {
  /**
   * The icon to display within the button (or button-link).
   * If provided, the icon will be displayed as an SVG.
   */
  icon?: string | null
  /**
   * An alternative text for the icon.
   * If provided and non-empty, the SVG will have a role="img" and an aria-label attribute.
   * If undefined or empty, the SVG will have an aria-hidden attribute instead, as a
   * decorative icon.
   */
  iconAlt?: string
  variant?: ButtonVariant
  iconPosition?: IconPositionEnum
  testId?: string
}
