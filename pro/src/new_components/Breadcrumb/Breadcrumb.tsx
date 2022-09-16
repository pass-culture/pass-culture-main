import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { ReactComponent as BreadcumbSeparator } from 'icons/ico-breadcrumb-arrow-right.svg'
import Stepper from 'new_components/Stepper'

import styles from './Breadcrumb.module.scss'
import type { Step } from './types'

export enum BreadcrumbStyle {
  DEFAULT = 'default',
  TAB = 'tab',
  STEPPER = 'stepper',
}

export interface IBreadcrumb {
  activeStep: string
  isDisabled?: boolean
  styleType?: BreadcrumbStyle
  steps: Step[]
  className?: string
}

const Breadcrumb = ({
  activeStep,
  isDisabled = false,
  styleType = BreadcrumbStyle.DEFAULT,
  steps,
  className,
}: IBreadcrumb): JSX.Element => {
  const breadcrumbClassName = cn(
    styles['pc-breadcrumb'],
    styles[`bc-${styleType}`]
  )
  className = isDisabled ? `${className} ${styles['bc-disabled']}` : className
  const lastStepIndex = steps.length - 1

  if (styleType === BreadcrumbStyle.STEPPER)
    return (
      <Stepper activeStep={activeStep} steps={steps} className={className} />
    )

  return (
    <ul
      className={cn(breadcrumbClassName, className)}
      data-testid={`bc-${styleType}`}
    >
      {steps.map((step, stepIndex) => {
        const isActive = activeStep === step.id
        const isLastStep = lastStepIndex === stepIndex

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
                step.label
              )}
            </span>

            {styleType === BreadcrumbStyle.DEFAULT && !isLastStep && (
              <div className={styles['separator']}>
                <BreadcumbSeparator />
              </div>
            )}
          </li>
        )
      })}
    </ul>
  )
}

export default Breadcrumb
