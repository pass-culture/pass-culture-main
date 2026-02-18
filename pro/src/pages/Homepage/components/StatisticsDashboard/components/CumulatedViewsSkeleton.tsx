import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import styles from './LoadingSkeleton.module.scss'

export const CumulatedViewsSkeleton = () => {
  return (
    <div className={styles['skeleton-stats']}>
      <div className={styles['skeleton-chart']}>
        <Skeleton height="1.5rem" width="60%" margin="0" />
        <Skeleton height="1rem" width="30%" margin="0.25rem 0 0 0" />
        <Skeleton height="18rem" width="100%" margin="1.5rem 0 0 0" />
      </div>

      <div className={styles['skeleton-offers']}>
        <Skeleton height="1.5rem" width="80%" margin="0" />
        <Skeleton height="1rem" width="50%" margin="0.25rem 0 0 0" />
        <Skeleton height="0.75rem" width="60%" margin="1.5rem 0 0 0" />

        <div className={styles['skeleton-offer-row']}>
          <Skeleton height="5rem" width="5rem" margin="0" />
          <div className={styles['skeleton-offer-text']}>
            <Skeleton height="0.75rem" width="90%" margin="0" />
            <Skeleton height="0.75rem" width="50%" margin="0.25rem 0 0 0" />
          </div>
        </div>
        <div className={styles['skeleton-offer-row']}>
          <Skeleton height="5rem" width="5rem" margin="0" />
          <div className={styles['skeleton-offer-text']}>
            <Skeleton height="0.75rem" width="90%" margin="0" />
            <Skeleton height="0.75rem" width="50%" margin="0.25rem 0 0 0" />
          </div>
        </div>
        <div className={styles['skeleton-offer-row']}>
          <Skeleton height="5rem" width="5rem" margin="0" />
          <div className={styles['skeleton-offer-text']}>
            <Skeleton height="0.75rem" width="90%" margin="0" />
            <Skeleton height="0.75rem" width="50%" margin="0.25rem 0 0 0" />
          </div>
        </div>
      </div>
    </div>
  )
}
