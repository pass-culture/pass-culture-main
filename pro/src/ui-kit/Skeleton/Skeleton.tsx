import cn from 'classnames'

import styles from './Skeleton.module.scss'

interface SkeletonProps {
  height?: string
  width?: string
  roundedFull?: boolean
  repeat?: number
}

export const Skeleton = ({
  height = '20px',
  width = '100%',
  roundedFull = false,
  repeat = 1,
}: SkeletonProps): JSX.Element => {
  const skeletons = new Array(repeat).fill(null)

  return (
    <div>
      <div className={styles['visually-hidden']}>Chargement en cours</div>
      {skeletons.map((_, index) => (
        <div
          data-testid={`skeleton`}
          aria-hidden={true}
          key={index}
          className={cn(styles.skeleton, {
            [styles['rounded-full']]: Boolean(roundedFull),
          })}
          style={{
            height,
            width,
          }}
        />
      ))}
    </div>
  )
}
