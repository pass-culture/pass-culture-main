import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Icon from '../../../../layout/Icon/Icon'
import formatDecimals from '../../../../../utils/numbers/formatDecimals'

class CreditGauge extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isGaugeEmpty: false
    }
  }

  componentDidMount() {
    const { currentAmount } = this.props

    this.greyGaugeWhenEmpty(currentAmount)
  }

  greyGaugeWhenEmpty = currentAmount => {
    if (currentAmount == 0) {
      this.setState({
        isGaugeEmpty: true
      })
    }
  }

  fillGaugue = (currentAmount, maxAmount) => {
    const ratio = (10 * currentAmount) / maxAmount
    const step = Math.floor(ratio)

    return `cg-gauge-width-${step}0`
  }

  render() {
    const { className, detailsText, picto, currentAmount, maxAmount } = this.props
    const { isGaugeEmpty } = this.state
    const currentWidth = this.fillGaugue(currentAmount, maxAmount)
    const formattedCurrentAmount = formatDecimals(currentAmount)

    return (
      <div
        className={`cg-container ${className} ${isGaugeEmpty ? 'cg-container-empty-gauge' : ''}`}
      >
        <div className="cg-gauge">
          <span className="cg-dot">
            <Icon svg={picto} />
          </span>
          <div className="cg-max">
            <div className={`cg-current  ${currentWidth}`} />
          </div>
        </div>
        <p className="cg-amount">
          {formattedCurrentAmount}
          &nbsp;
          {'€'}
        </p>
        <p>
          {detailsText}
        </p>
      </div>
    )
  }
}

CreditGauge.propTypes = {
  className: PropTypes.string.isRequired,
  currentAmount: PropTypes.number.isRequired,
  detailsText: PropTypes.string.isRequired,
  maxAmount: PropTypes.number.isRequired,
  picto: PropTypes.string.isRequired
}

export default CreditGauge
