import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { ReactComponent as BreadcumbSeparator } from 'icons/ico-breadcrumb-arrow-right.svg'

import type { Step } from './types'

export enum BreadcrumbStyle {
  DEFAULT = 'default',
  TAB = 'tab',
}

interface IBreadcrumb {
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
  const breadcrumbClassName = `pc-breadcrumb bc-${styleType}`
  className = isDisabled ? `${className} bc-disabled` : className
  const lastStepIndex = steps.length - 1

  return (
    <ul className={cn(breadcrumbClassName, className)}>
      {steps.map((step, stepIndex) => {
        const isActive = activeStep === step.id
        const isLastStep = lastStepIndex === stepIndex

        return (
          <li
            className={`bc-step ${isActive ? 'active' : ''}`}
            key={`breadcrumb-step-${step.id}`}
          >
            <span className="bcs-label" key={`breadcrumb-step-${step.id}`}>
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
              <div className="separator">
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
