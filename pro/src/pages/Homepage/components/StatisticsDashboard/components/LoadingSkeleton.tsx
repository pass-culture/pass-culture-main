import { Skeleton } from 'ui-kit/Skeleton/Skeleton'

import styles from './LoadingSkeleton.module.scss'

export function LoadingSkeleton() {
  return (
    <div className={styles['skeleton-wrapper']}>
      <Skeleton height="2.5rem" width="2rem" />
      <div className={styles['skeleton-line']}>
        <Skeleton height="1rem" width="100%" />
        <Skeleton height="1rem" width="80%" />
      </div>
    </div>
  )
}
