import cn from 'classnames'

import styles from './BubbleStepper.module.scss'

type BubbleStepperProps = {
  total: number
  page: number
  className?: string
}

export const BubbleStepper = ({
  total,
  page,
  className,
}: BubbleStepperProps): JSX.Element => {
  return (
    <div className={cn(styles.wrapper, className)}>
      {Array.from({ length: total }, (_, i) => i + 1).map((index) => (
        <div
          key={index}
          className={cn(styles.bubble, {
            [styles.active]: index === page,
          })}
        ></div>
      ))}
    </div>
  )
}
