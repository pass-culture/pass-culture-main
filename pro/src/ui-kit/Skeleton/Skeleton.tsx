import cn from 'classnames'

import styles from './Skeleton.module.scss'

interface SkeletonProps {
  height?: string
  width?: string
  roundedFull?: boolean
}

export const Skeleton = ({
  height = '1.5rem',
  width = '100%',
  roundedFull = false,
}: SkeletonProps): JSX.Element => {
  return (
    <div>
      <div className={styles['visually-hidden']}>Chargement en cours</div>
      <div
        data-testid={`skeleton`}
        aria-hidden={true}
        className={cn(styles.skeleton, {
          [styles['rounded-full']]: Boolean(roundedFull),
        })}
        style={{
          height,
          width,
        }}
      />
    </div>
  )
}
