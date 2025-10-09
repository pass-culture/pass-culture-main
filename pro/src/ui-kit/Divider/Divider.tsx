import classnames from 'classnames'
import type { FC } from 'react'

import styles from './Divider.module.scss'

/**
 * Size options for the Divider component.
 */
type Size = 'medium' | 'large'

/**
 * Props for the Divider component.
 */
interface DividerProps {
  /**
   * The size of the divider, determining its thickness.
   * @default 'medium'
   */
  size?: Size
  /**
   * Orientation of the divider,
   * @default 'horizontal'
   */
  orientation?: 'horizontal' | 'vertical'
  /**
   * Custom CSS class for additional styling of the divider.
   */
  className?: string
}

/**
 * The Divider component is used to visually separate content within a page.
 * It supports different sizes for varying use cases, and allows for custom styling.
 *
 * ---
 * **Important: Use the `size` prop to adjust the divider's visual weight according to the content.**
 * ---
 *
 * @param {DividerProps} props - The props for the Divider component.
 * @returns {JSX.Element} The rendered Divider component.
 *
 * @example
 * <Divider size="large" />
 *
 */
export const Divider: FC<DividerProps> = ({
  size,
  orientation = 'horizontal',
  className,
}) => {
  const sizeClassName = {
    medium: styles['divider-medium'],
    large: styles['divider-large'],
  }[size || 'medium']

  return (
    <div
      className={classnames(
        styles.divider,
        sizeClassName,
        styles[orientation],
        className
      )}
    />
  )
}
