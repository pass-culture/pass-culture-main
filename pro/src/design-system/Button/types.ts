export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERTIARY = 'tertiary',
}

export enum IconPositionEnum {
  LEFT = 'left',
  RIGHT = 'right',
}

export enum ButtonColor {
  BRAND = 'brand',
  NEUTRAL = 'neutral',
}

export enum ButtonSize {
  DEFAULT = 'default',
  SMALL = 'small',
}

/**
 * ******************* Base props *******************
 */
interface ButtonBaseProps {
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
   * If the button is disabled
   */
  disabled?: boolean
  /**
   * If the button is hovered
   */
  hovered?: boolean
  /**
   * If the button is loading
   */
  isLoading?: boolean
  /**
   * The size of the button
   */
  size?: ButtonSize
  /**
   * If the button has a transparent background (principally used with secondary variant)
   */
  transparent?: boolean
  /**
   * If the button is full width
   */
  fullWidth?: boolean
  /**
   * If the button is full height
   */
  fullHeight?: boolean
  /**
   * The tooltip of the button
   */
  tooltip?: string
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
}

/**
 * ******************* Button props *******************
 */
type ButtonAsButtonProps = ButtonBaseProps & {
  /**
   * The type of component
   */
  as?: 'button'
  /**
   * The type of the button
   */
  type?: ButtonTypeAttribute
  to?: never
  opensInNewTab?: never
  isExternal?: never
  isSectionLink?: never
} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'disabled'>

/**
 * ******************* Link props *******************
 */
type ButtonAsLinkProps = ButtonBaseProps & {
  as: 'a'
  type?: never
  to: string
  opensInNewTab?: boolean
  isExternal?: boolean
  isSectionLink?: boolean
} & Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, 'href'>

export type ButtonTypeAttribute =
  React.ButtonHTMLAttributes<HTMLButtonElement>['type']

export type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps
