import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import Stepper from 'components/Stepper'

import styles from './Breadcrumb.module.scss'
import type { Step } from './types'

export enum BreadcrumbStyle {
  TAB = 'tab',
  STEPPER = 'stepper',
}

export interface BreadcrumbProps {
  activeStep: string
  isDisabled?: boolean
  styleType?: BreadcrumbStyle
  steps: Step[]
  className?: string
}

const Breadcrumb = ({
  activeStep,
  isDisabled = false,
  styleType = BreadcrumbStyle.TAB,
  steps,
  className,
}: BreadcrumbProps): JSX.Element => {
  const breadcrumbClassName = cn(
    styles['pc-breadcrumb'],
    styles[`bc-${styleType}`]
  )
  className = isDisabled ? `${className} ${styles['bc-disabled']}` : className

  if (styleType === BreadcrumbStyle.STEPPER) {
    return (
      <Stepper activeStep={activeStep} steps={steps} className={className} />
    )
  }

  return (
    <ul
      className={cn(breadcrumbClassName, className)}
      data-testid={`bc-${styleType}`}
    >
      {steps.map((step) => {
        const isActive = activeStep === step.id

        return (
          <li
            className={cn(styles['bc-step'], isActive && styles['active'])}
            key={`breadcrumb-step-${step.id}`}
            data-testid={`breadcrumb-step-${step.id}`}
          >
            <span
              className={styles['bcs-label']}
              key={`breadcrumb-step-${step.id}`}
            >
              {step.url ? (
                <Link
                  onClick={step.onClick ? step.onClick : undefined}
                  to={step.url}
                >
                  {step.label}
                </Link>
              ) : step.hash ? (
                <a
                  href={`#${step.hash}`}
                  onClick={step.onClick ? step.onClick : undefined}
                >
                  {step.label}
                </a>
              ) : (
                <span>{step.label}</span>
              )}
            </span>
          </li>
        )
      })}
    </ul>
  )
}

export default Breadcrumb
