import cn from 'classnames'
import React, { createElement } from 'react'

import styles from './HelpSection.module.scss'
import { Step1SVG } from './Step1SVG'
import { Step2SVG } from './Step2SVG'
import { Step3SVG } from './Step3SVG'

interface StepProps {
  stepNumber: number
  image: React.ElementType
  content: string
}

const Step = ({ stepNumber, image, content }: StepProps) => (
  <li className={styles['step']}>
    <div className={styles['step-hero']}>
      <div className={styles['step-number']}>{stepNumber}</div>
      {createElement(image, { className: styles['step-image'] })}
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
        image={Step1SVG}
        content="Ajoutez une ou plusieurs dates et le nombre de places"
      />

      <Step
        stepNumber={2}
        image={Step2SVG}
        content="Visualisez les dates créées"
      />

      <Step
        stepNumber={3}
        image={Step3SVG}
        content="Si besoin, ajoutez de nouvelles dates"
      />
    </ol>
  </section>
)
