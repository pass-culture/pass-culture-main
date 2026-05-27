export enum LinkSize {
  DEFAULT = 'default',
  SMALL = 'small',
  EXTRA_SMALL = 'extra-small',
}

export enum LinkColor {
  BRAND = 'brand',
  NEUTRAL = 'neutral',
}

export type LinkProps = {
  /**
   * The label of the link. It should be explicit and describe the destination or action. Avoid generic wording such as "Click here".
   */
  label: string
  /**
   * The destination URL.
   */
  to: string
  /**
   * The icon of the link.
   */
  icon?: string
  /**
   * Optional function to call when the link is clicked.
   */
  onClick?: () => void
  /**
   * The color of the link.
   * @default LinkColor.BRAND
   */
  color?: LinkColor
  /**
   * If true, the link will be rendered as an `<a>` tag pointing to an external URL. Otherwise, it will use the React Router `Link` component.
   * @default false
   */
  isExternalLink?: boolean
  /**
   * If true, the link will open in a new tab.
   * @default false
   */
  shouldOpenNewTab?: boolean
  /**
   * The size of the link.
   * @default LinkSize.DEFAULT
   */
  size?: LinkSize
}
