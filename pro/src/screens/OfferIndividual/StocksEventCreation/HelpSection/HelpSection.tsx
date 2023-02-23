import cn from 'classnames'
import React from 'react'

import styles from './HelpSection.module.scss'
import step1 from './step1.svg'
import step2 from './step2.svg'
import step3 from './step3.svg'

interface StepProps {
  stepNumber: number
  image: string
  content: string
}

const Step = ({ stepNumber, image, content }: StepProps) => (
  <li className={styles['step']}>
    <div className={styles['step-hero']}>
      <div className={styles['step-number']}>{stepNumber}</div>
      <img src={image} alt="" className={styles['step-image']} />
    </div>
    {content}
  </li>
)

interface Props {
  className?: string
}

export const HelpSection = ({ className }: Props): JSX.Element => (
  <section className={cn(styles['container'], className)}>
    <h2 className={styles['title']}>Comment faire ?</h2>

    <ol className={styles['steps-list']}>
      <Step
        stepNumber={1}
        image={step1}
        content="Ajoutez une récurrence et le nombre de places"
      />

      <Step
        stepNumber={2}
        image={step2}
        content="Visualisez les occurrences créées"
      />

      <Step
        stepNumber={3}
        image={step3}
        content="Si besoin, ajoutez une nouvelle récurrence"
      />
    </ol>
  </section>
)
