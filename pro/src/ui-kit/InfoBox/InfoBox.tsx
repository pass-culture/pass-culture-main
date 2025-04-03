import cn from 'classnames'
import { ReactNode } from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink, LinkProps } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ShadowTipsHelpIcon } from 'ui-kit/Icons/SVGs/ShadowTipsHelpIcon'

import styles from './InfoBox.module.scss'

/**
 * Props for the link inside the InfoBox component.
 *
 * @extends LinkProps
 */
interface InfoBoxLinkProps extends LinkProps {
  /**
   * The text to display for the link.
   */
  text: string
}

/**
 * Props for the InfoBox component.
 */
interface InfoBoxProps {
  /**
   * The content to display inside the InfoBox.
   */
  children: ReactNode
  /**
   * An optional link to include in the InfoBox.
   */
  link?: InfoBoxLinkProps
  className?: string
}

/**
 * The InfoBox component is used to present key information or tips to users, optionally including a link for further action.
 * It contains a title, text content, and can also include a button link.
 *
 * ---
 * **Important: Use the `link` prop to provide additional resources or actions for the information presented.**
 * ---
 *
 * @param {InfoBoxProps} props - The props for the InfoBox component.
 * @returns {JSX.Element} The rendered InfoBox component.
 *
 * @example
 * <InfoBox link={{ to: '/learn-more', text: 'Learn More' }}>
 *   This is some important information you should know.
 * </InfoBox>
 *
 * @accessibility
 * - **Consistent Styling**: Ensure the InfoBox styling maintains a good color contrast ratio for accessibility.
 * - **Icon Usage**: The `ShadowTipsHelpIcon` is used to visually emphasize the content's informative nature. Provide meaningful ARIA labels if needed.
 */
export const InfoBox = ({
  children,
  link,
  className,
}: InfoBoxProps): JSX.Element => {
  return (
    <div className={cn(className, styles['info-box'])}>
      <div className={styles['info-box-header']}>
        <div className={cn(styles['info-box-bar'])} />
        <div className={styles['info-box-title']}>
          <ShadowTipsHelpIcon className={styles['info-box-title-icon']} />
          <span>À SAVOIR</span>
        </div>
        <div className={cn(styles['info-box-bar'])} />
      </div>

      <p className={styles['info-box-text']}>{children}</p>

      {link && (
        <ButtonLink
          {...link}
          icon={fullLinkIcon}
          className={styles['info-box-link']}
          variant={ButtonVariant.QUATERNARY}
        >
          {link.text}
        </ButtonLink>
      )}
    </div>
  )
}
