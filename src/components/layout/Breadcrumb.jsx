import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { ReactComponent as BreadcumbSeparator } from 'icons/ico-breadcrumb-arrow-right.svg'

export const STYLE_TYPE_DEFAULT = 'default'
export const STYLE_TYPE_TAB = 'tab'

const Breadcrumb = props => {
  const { activeStep, styleType, steps } = props

  const lastStepIndex = steps.length - 1
  return (
    <div className={`pc-breadcrumb bc-${styleType}`}>
      {steps.map((step, stepIndex) => {
        const isActive = activeStep === step.id
        const isLastStep = lastStepIndex === stepIndex

        return (
          <span
            className={`bc-step ${isActive ? 'active' : ''}`}
            key={`breadcrumb-step-${step.id}`}
          >
            <span
              className="bcs-label"
              key={`breadcrumb-step-${step.id}`}
            >
              {step.url ? (
                <Link to={step.url}>
                  {step.label}
                </Link>
              ) : step.label}

              <span className="active-underline" />
            </span>

            {styleType === STYLE_TYPE_DEFAULT && !isLastStep && (
              <div className="separator">
                <BreadcumbSeparator />
              </div>
            )}
          </span>
        )
      })}
    </div>
  )
}

Breadcrumb.defaultProps = {
  styleType: STYLE_TYPE_DEFAULT,
}

Breadcrumb.propTypes = {
  activeStep: PropTypes.string.isRequired,
  steps: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      url: PropTypes.string,
    })
  ).isRequired,
  styleType: PropTypes.oneOf([STYLE_TYPE_DEFAULT, STYLE_TYPE_TAB]),
}

export default Breadcrumb
