export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERNARY = 'ternary',
  TERNARYBRAND = 'ternary-brand',
  QUATERNARY = 'quaternary',
  BOX = 'box',
}

export enum IconPositionEnum {
  RIGHT = 'right',
  LEFT = 'left',
  CENTER = 'center',
}

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
