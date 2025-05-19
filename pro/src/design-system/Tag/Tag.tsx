import cx from 'classnames'

import bookIcon from 'icons/full-book.svg'
import headlineIcon from 'icons/full-boosted.svg'
import likeIcon from 'icons/full-thumb-up.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Tag.module.scss'

export enum TagVariant {
  DEFAULT = 'default',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  NEW = 'new',
}

export enum TagSpecificVariant {
  BOOKCLUB = 'bookclub',
  HEADLINE = 'headline',
  LIKE = 'like',
}

const tagIconBySpecificVariant: Record<TagSpecificVariant, string> = {
  [TagSpecificVariant.BOOKCLUB]: bookIcon,
  [TagSpecificVariant.HEADLINE]: headlineIcon,
  [TagSpecificVariant.LIKE]: likeIcon,
}

interface TagProps {
  /**
   * The label of the tag.
   */
  label: string
  /**
   * The variant of the tag, which determines its style.
   */
  variant?: TagVariant | TagSpecificVariant
  /**
   * Optional prop to pass a custom icon for the tag.
   * Only works for default, success, warning, and error variants.
   */
  icon?: string
  /**
   * Optional className for additional styling.
   */
  className?: string
}

export const Tag = ({
  label,
  variant = TagVariant.DEFAULT,
  icon,
  className,
}: TagProps): JSX.Element => {
  const finalIcon = Object.keys(tagIconBySpecificVariant).includes(variant)
    ? tagIconBySpecificVariant[variant as TagSpecificVariant]
    : variant !== TagVariant.NEW && icon

  return (
    <span className={cx(styles.tag, styles[variant], className)}>
      {finalIcon && (
        <SvgIcon className={styles.icon} src={finalIcon} width="16" />
      )}
      {label}
    </span>
  )
}
