import cx from 'classnames'
import { ReactNode } from 'react'

import styles from './Tag.module.scss'

export enum TagVariant {
  SMALL_OUTLINE = 'small-outline',
  LIGHT_GREY = 'light-grey',
  DARK_GREY = 'dark-grey',
  BLACK = 'black',
  PURPLE = 'purple',
  LIGHT_PURPLE = 'light-purple',
  RED = 'red',
  GREEN = 'green',
  BLUE = 'blue',
  LIGHT_GREEN = 'light-green',
  LIGHT_YELLOW = 'light-yellow',
  LIGHT_BLUE = 'light-blue',
}

const classByVariant: Record<TagVariant, string> = {
  [TagVariant.SMALL_OUTLINE]: styles['small-outline'],
  [TagVariant.LIGHT_GREY]: styles['light-grey'],
  [TagVariant.DARK_GREY]: styles['dark-grey'],
  [TagVariant.BLACK]: styles['black'],
  [TagVariant.PURPLE]: styles['purple'],
  [TagVariant.LIGHT_PURPLE]: styles['light-purple'],
  [TagVariant.RED]: styles['red'],
  [TagVariant.GREEN]: styles['green'],
  [TagVariant.BLUE]: styles['blue'],
  [TagVariant.LIGHT_GREEN]: styles['light-green'],
  [TagVariant.LIGHT_YELLOW]: styles['light-yellow'],
  [TagVariant.LIGHT_BLUE]: styles['light-blue'],
}

/**
 * Props for the Tag component.
 */
interface TagProps {
  /**
   * Custom CSS class for additional styling of the tag.
   */
  className?: string
  /**
   * The content to be displayed inside the tag.
   */
  children: ReactNode
  /**
   * The variant of the tag, which determines its style.
   */
  variant: TagVariant
}

/**
 * The Tag component is used to display a label with a specific variant styling.
 * It supports different colors and styles to convey various statuses or categories.
 *
 * ---
 * **Important: Use the `variant` prop to select the appropriate style for the tag.**
 * ---
 *
 * @param {TagProps} props - The props for the Tag component.
 * @returns {JSX.Element} The rendered Tag component.
 *
 * @example
 * <Tag variant={TagVariant.RED}>Urgent</Tag>
 *
 * @accessibility
 * - **Visual Differentiation**: Different variants provide visual cues to help users understand the context or status associated with the tag.
 */
export const Tag = ({
  children,
  className,
  variant,
}: TagProps): JSX.Element => (
  <span className={cx(styles['tag'], classByVariant[variant], className)}>
    {children}
  </span>
)
