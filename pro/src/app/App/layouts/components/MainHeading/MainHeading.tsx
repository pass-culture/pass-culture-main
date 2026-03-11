/** biome-ignore-all lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */
import cn from 'classnames'
import type { ReactNode } from 'react'

import styles from './MainHeading.module.scss'

interface MainHeadingProps {
  className?: string
  mainHeading: ReactNode
  mainSubHeading?: string
}

export const MainHeading = ({
  className,
  mainHeading,
  mainSubHeading,
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
    </div>
  )
}
