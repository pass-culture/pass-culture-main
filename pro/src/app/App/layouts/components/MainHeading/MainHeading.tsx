/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type { JSX } from 'react'

import { BackToNavLink } from '@/components/BackToNavLink/BackToNavLink'

import styles from './MainHeading.module.scss'

interface MainHeadingProps {
  className?: string
  mainHeading: React.ReactNode
  mainSubHeading?: string
  isConnected?: boolean
}

export const MainHeading = ({
  className,
  mainHeading,
  mainSubHeading,
  isConnected = true,
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
      {isConnected && (
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
