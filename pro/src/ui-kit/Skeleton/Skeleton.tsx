import cn from 'classnames'
import type { JSX } from 'react'

import styles from './Skeleton.module.scss'

interface SkeletonProps {
  height?: string
  width?: string
  margin?: string
  roundedFull?: boolean
}

export const Skeleton = ({
  height = '1.5rem',
  width = '100%',
  roundedFull = false,
  margin = '0.5rem 0',
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
          margin,
        }}
      />
    </div>
  )
}
