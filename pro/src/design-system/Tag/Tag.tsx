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
  BOOKCLUB = 'bookclub',
  CINECLUB = 'cineclub',
  HEADLINE = 'headline',
  LIKE = 'like',
}

const tagIconByVariant: { [key in TagVariant]?: string } = {
  [TagVariant.BOOKCLUB]: bookIcon,
  [TagVariant.CINECLUB]: bookIcon,
  [TagVariant.HEADLINE]: headlineIcon,
  [TagVariant.LIKE]: likeIcon,
}

export type TagProps = {
  /**
   * The label of the tag.
   */
  label: string
  /**
   * The variant of the tag, which determines its style.
   */
  variant?: TagVariant
  /**
   * Optional prop to pass a custom icon for the tag.
   * Only works for default, success, warning, and error variants.
   */
  icon?: string
}

export const Tag = ({
  label,
  variant = TagVariant.DEFAULT,
  icon,
}: TagProps): JSX.Element => {
  const finalIcon =
    tagIconByVariant[variant as TagVariant] ||
    (variant !== TagVariant.NEW && icon)

  return (
    <span className={cx(styles.tag, styles[variant])}>
      {finalIcon && (
        <SvgIcon className={styles.icon} src={finalIcon} width="16" />
      )}
      {label}
    </span>
  )
}
