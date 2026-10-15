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
    <ol
      aria-label="Progression du parcours"
      className={cn(styles.wrapper, className)}
    >
      {Array.from({ length: total }, (_, i) => i + 1).map((index) => {
        const isCurrentStep = index === page
        const stepNotNow = index < page ? 'terminée' : 'à venir'
        const stepState = isCurrentStep ? 'active' : stepNotNow

        return (
          <li key={index} aria-current={isCurrentStep ? 'step' : undefined}>
            <span className={styles['visually-hidden']}>
              Étape {index} sur {total}, {stepState}
            </span>
            <span
              aria-hidden="true"
              className={cn(styles.bubble, {
                [styles.active]: isCurrentStep,
              })}
            />
          </li>
        )
      })}
    </ol>
  )
}
