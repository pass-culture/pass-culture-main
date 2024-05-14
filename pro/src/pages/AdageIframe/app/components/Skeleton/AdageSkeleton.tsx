import styles from './AdageSkeleton.module.scss'

const AdageSkeleton = ({ isGrid = false }: { isGrid?: boolean }) => {
  return (
    <>
      {isGrid ? (
        <div className={styles['skeleton-grid']} data-testid="spinner">
          <div className={styles['skeleton-grid-image']}></div>
          <div className={styles['skeleton-grid-info']}>
            <div className={styles['skeleton-grid-tag']}></div>
            <div className={styles['skeleton-grid-tag']}></div>
          </div>
          <div className={styles['skeleton-grid-title']}></div>
          <div className={styles['line-description']}></div>
          <div className={styles['line-50']}></div>
        </div>
      ) : (
        <div className={styles['skeleton-list']} data-testid="spinner">
          <div className={styles['skeleton-list-image']}></div>
          <div className={styles['skeleton-list-text']}>
            <div className={styles['skeleton-list-header']}>
              <div className={styles['skeleton-list-info']}>
                <div className={styles['skeleton-list-tag']}></div>
                <div className={styles['skeleton-list-tag']}></div>
                <div className={styles['skeleton-list-tag']}></div>
                <div className={styles['skeleton-list-tag']}></div>
              </div>
              <div className={styles['skeleton-list-actions']}>
                <div className={styles['skeleton-list-button']}></div>
                <div className={styles['skeleton-list-button']}></div>
              </div>
            </div>
            <div className={styles['skeleton-list-title']}></div>
            <div className={styles['line']}></div>
            <div className={styles['line-25']}></div>
            <div className={styles['line-description']}></div>
            <div className={styles['line-description']}></div>
          </div>
        </div>
      )}
    </>
  )
}

export default AdageSkeleton
