/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type { ReactNode } from 'react'

import { BackToNavLink } from './BackToNavLink/BackToNavLink'
import styles from './MainHeading.module.scss'

interface MainHeadingProps {
  className?: string
  mainHeading: ReactNode
  mainSubHeading?: string
  /**
   * Whether to display a "Back to navigation" link under the heading.
   * We expect this link in connected layouts, and as long as the navigation
   * is rendered.
   */
  shouldDisplayBackToNavLink?: boolean
}

export const MainHeading = ({
  className,
  mainHeading,
  mainSubHeading,
  shouldDisplayBackToNavLink,
}: MainHeadingProps): JSX.Element => {
  return (
    <div
      className={cn(className, styles['main-heading-wrapper'], {
        [styles['main-heading-wrapper-with-subtitle']]: mainSubHeading,
      })}
    >
      <h1 className={styles['main-heading-title']}>
        {mainHeading}
        {mainSubHeading && (
          <span className={styles['main-heading-subtitle']}>
            {mainSubHeading}
          </span>
        )}
      </h1>
      {shouldDisplayBackToNavLink && (
        <BackToNavLink
          className={cn(styles['main-heading-back-to-nav-link'], {
            [styles['main-heading-back-to-nav-link-with-subtitle']]:
              mainSubHeading,
          })}
        />
      )}
    </div>
  )
}
