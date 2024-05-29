import styles from './AdageSkeleton.module.scss'

export const AdageSkeleton = ({ isGrid = false }: { isGrid?: boolean }) => {
  return (
    <>
      {isGrid ? (
        <div className={styles['skeleton-grid']} data-testid="spinner">
          <div className={styles['skeleton-grid-image']} />
          <div className={styles['skeleton-grid-info']}>
            <div className={styles['skeleton-grid-tag']} />
            <div className={styles['skeleton-grid-tag']} />
          </div>
          <div className={styles['skeleton-grid-title']} />
          <div className={styles['line-description']} />
          <div className={styles['line-50']} />
        </div>
      ) : (
        <div className={styles['skeleton-list']} data-testid="spinner">
          <div className={styles['skeleton-list-image']} />
          <div className={styles['skeleton-list-text']}>
            <div className={styles['skeleton-list-header']}>
              <div className={styles['skeleton-list-info']}>
                <div className={styles['skeleton-list-tag']} />
                <div className={styles['skeleton-list-tag']} />
                <div className={styles['skeleton-list-tag']} />
                <div className={styles['skeleton-list-tag']} />
              </div>
              <div className={styles['skeleton-list-actions']}>
                <div className={styles['skeleton-list-button']} />
                <div className={styles['skeleton-list-button']} />
              </div>
            </div>
            <div className={styles['skeleton-list-title']} />
            <div className={styles['line']} />
            <div className={styles['line-25']} />
            <div className={styles['line-description']} />
            <div className={styles['line-description']} />
          </div>
        </div>
      )}
    </>
  )
}
