import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import Stepper from 'components/Stepper'
import fullArrowRightIcon from 'icons/full-arrow-right.svg'
import fullErrorIcon from 'icons/full-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Breadcrumb.module.scss'
import type { Step } from './types'

export enum BreadcrumbStyle {
  DEFAULT = 'default',
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
  styleType = BreadcrumbStyle.DEFAULT,
  steps,
  className,
}: BreadcrumbProps): JSX.Element => {
  const breadcrumbClassName = cn(
    styles['pc-breadcrumb'],
    styles[`bc-${styleType}`]
  )
  className = isDisabled ? `${className} ${styles['bc-disabled']}` : className
  const lastStepIndex = steps.length - 1

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
                  {step.hasWarning && (
                    <SvgIcon
                      src={fullErrorIcon}
                      alt=""
                      width="20"
                      className={styles['error-icon']}
                    />
                  )}
                </Link>
              ) : step.hash ? (
                <a
                  href={`#${step.hash}`}
                  onClick={step.onClick ? step.onClick : undefined}
                >
                  {step.label}
                  {step.hasWarning && (
                    <SvgIcon
                      src={fullErrorIcon}
                      alt=""
                      width="20"
                      className={styles['error-icon']}
                    />
                  )}
                </a>
              ) : (
                <span>
                  step.label
                  {step.hasWarning && (
                    <SvgIcon
                      src={fullErrorIcon}
                      alt=""
                      width="20"
                      className={styles['error-icon']}
                    />
                  )}
                </span>
              )}
            </span>

            {styleType === BreadcrumbStyle.DEFAULT && !isLastStep && (
              <div className={styles['separator']}>
                <SvgIcon
                  src={fullArrowRightIcon}
                  alt=""
                  className={styles['separator-icon']}
                />
              </div>
            )}
          </li>
        )
      })}
    </ul>
  )
}

export default Breadcrumb
