import cn from 'classnames'
import React from 'react'

import styles from './Skeleton.module.scss'

// Define the prop types for the Skeleton component
interface SkeletonProps {
  height?: string
  width?: string
  className?: string
  inline?: boolean // Optional prop to make the skeleton inline
  repeat?: number // Prop to specify how many times the skeleton should be repeated
}

// Skeleton Component
export const Skeleton: React.FC<SkeletonProps> = ({
  height = '20px',
  width = '100%',
  className = '',
  repeat = 1, // Default value is 1
}) => {
  // Create an array of Skeleton elements based on the repeat prop
  const skeletons = new Array(repeat).fill(null)

  return (
    <div className={cn(styles.skeletonWrapper, className)}>
      {skeletons.map((_, index) => (
        <div
          key={index}
          className={cn(styles.skeleton)}
          style={{
            height,
            width,
          }}
        />
      ))}
    </div>
  )
}
