import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../../../layout/Icon/Icon'
import formatDecimals from '../../../../../utils/numbers/formatDecimals'

const NON_BREAKING_SPACE = '\u00A0'

const CreditGauge = ({ extraClassName, creditLimit, detailsText, picto, remainingCredit }) => {
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
      <p className="cg-written-remaining">
        {`${formattedRemainingCredit}${NON_BREAKING_SPACE}€`}
      </p>
      <p>
        {detailsText}
      </p>
    </div>
  )
}

export const computeFillingStep = (remainingCredit, creditLimit) => {
  const ratio = (10 * remainingCredit) / creditLimit
  const step = Math.floor(ratio)

  return step
}

CreditGauge.propTypes = {
  creditLimit: PropTypes.number.isRequired,
  detailsText: PropTypes.string.isRequired,
  extraClassName: PropTypes.string.isRequired,
  picto: PropTypes.string.isRequired,
  remainingCredit: PropTypes.number.isRequired
}

export default CreditGauge
