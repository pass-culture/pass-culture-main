import { Skeleton } from 'ui-kit/Skeleton/Skeleton'

import styles from './LoadingSkeleton.module.scss'

export function LoadingSkeleton() {
  return (
    <div className={styles['skeleton-wrapper']}>
      <Skeleton height="40px" width="30px" />
      <div className={styles['skeleton-line']}>
        <Skeleton height="16px" width="100%" />
        <Skeleton height="14px" width="80%" />
      </div>
    </div>
  )
}
