export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERTIARY = 'tertiary',
}

export enum IconPositionEnum {
  LEFT = 'left',
  RIGHT = 'right',
  CENTER = 'center',
}

export enum ButtonColor {
  BRAND = 'brand',
  NEUTRAL = 'neutral',
}

export enum ButtonSize {
  DEFAULT = 'default',
  SMALL = 'small',
}

export enum ButtonType {
  BUTTON = 'button',
  SUBMIT = 'submit',
  RESET = 'reset',
}

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * The color of the button
   */
  color?: ButtonColor
  /**
   * The variant of the button
   */
  variant?: ButtonVariant
  /**
   * The label of the button
   */
  label?: string
  /**
   * Whether the button is disabled
   */
  disabled?: boolean
  /**
   * Whether the button is hovered
   */
  hovered?: boolean
  /**
   * Whether the button is loading
   */
  isLoading?: boolean
  /**
   * The size of the button
   */
  size?: ButtonSize
  /**
   * The type of the button
   */
  type?: ButtonType
  /**
   * Whether the button has a transparent background (principally used with secondary variant)
   */
  transparent?: boolean
  /**
   * Whether the button is full width
   */
  fullWidth?: boolean
  /**
   ******************* Icon props *******************
   */
  /**
   * The icon of the button
   */
  icon?: string
  /**
   * The alternative text of the icon
   */
  iconAlt?: string
  /**
   * The position of the icon
   */
  iconPosition?: IconPositionEnum
  /**
   * The class name of the icon
   */
  iconClassName?: string
  /**
   * ******************* Link props *******************
   */
  /**
   * The destination URL for the link
   */
  to?: string
  /**
   * If `true` the link will open in a new tab and the new tab icon will be displayed with an accessible label.
   */
  opensInNewTab?: boolean
  /**
   * If `true` the link is external
   */
  isExternal?: boolean
  /**
   * If `true` the link is a section link
   */
  isSectionLink?: boolean
}
