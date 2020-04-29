import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../../../layout/Icon/Icon'
import formatDecimals from '../../../../../utils/numbers/formatDecimals'
import { NON_BREAKING_SPACE } from '../../../../../utils/specialCharacters'

const CreditGauge = ({ children, extraClassName, creditLimit, picto, remainingCredit }) => {
  const isGaugeEmpty = remainingCredit === 0
  const fillingStep = computeFillingStep(remainingCredit, creditLimit)
  const formattedRemainingCredit = formatDecimals(remainingCredit)

  return (
    <div
      className={`cg-container ${extraClassName} ${isGaugeEmpty ? 'cg-container-empty-gauge' : ''}`}
    >
      <div className="cg-gauge">
        <span className="cg-circle">
          <Icon svg={picto} />
        </span>
        <div className="cg-limit">
          <div className={`cg-remaining cg-gauge-width-${fillingStep}`} />
        </div>
      </div>
      <div className="cg-written-remaining">
        {`${formattedRemainingCredit}${NON_BREAKING_SPACE}€`}
      </div>
      <pre className="cg-pre">
        {children}
      </pre>
    </div>
  )
}

export const computeFillingStep = (remainingCredit, creditLimit) => {
  const ratio = (10 * remainingCredit) / creditLimit
  const step = Math.floor(ratio)

  return step
}

CreditGauge.propTypes = {
  children: PropTypes.node.isRequired,
  creditLimit: PropTypes.number.isRequired,
  extraClassName: PropTypes.string.isRequired,
  picto: PropTypes.string.isRequired,
  remainingCredit: PropTypes.number.isRequired,
}

export default CreditGauge
