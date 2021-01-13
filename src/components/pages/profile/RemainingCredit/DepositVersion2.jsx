import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import { getRemainingCreditForGivenCreditLimit } from '../domain/getRemainingCreditForGivenCreditLimit'
import CreditGauge from './CreditGauge/CreditGauge'
import User from '../ValueObjects/User'

class DepositVersion2 extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isReadMoreVisible: false,
    }
  }

  handleToggleReadMore = () => {
    this.setState(previousState => ({ isReadMoreVisible: !previousState.isReadMoreVisible }))
  }

  render() {
    const { user } = this.props
    const { isReadMoreVisible } = this.state
    const { expenses, wallet_balance: walletBalance } = user

    // Gauge ALL
    let initialDeposit = 0
    if (expenses.length) {
      const all = expenses.find(expense => expense.domain === 'all')
      initialDeposit = all.limit
    }

    const totalGaugeProperties = {
      creditLimit: initialDeposit,
      remainingCredit: walletBalance,
    }
    // Gauge ALL

    let digitalCreditLimit = 0
    let digitalRemainingCredit = 0
    if (expenses.length) {
      const digital = expenses.find(expense => expense.domain === 'digital')
      digitalCreditLimit = digital.limit
      digitalRemainingCredit = getRemainingCreditForGivenCreditLimit(walletBalance)(digital)
    }

    const digitalGaugeProperties = {
      creditLimit: digitalCreditLimit,
      remainingCredit: digitalRemainingCredit,
    }

    return (
      <section className="pf-section">
        <div className="rc-informations-container">
          <div className="rc-gauges-container">
            <div className="rc-gauges-title">
              {`Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`}
            </div>
            <div className="rc-gauges">
              <CreditGauge
                extraClassName="gauge-digital"
                picto="picto-digital-good"
                {...digitalGaugeProperties}
              >
                {`en offres\u000Anumériques\u000A(streaming…)`}
              </CreditGauge>
              <CreditGauge
                extraClassName="gauge-total"
                picto="picto-all-goods"
                {...totalGaugeProperties}
              >
                {`en sorties et\u000Abiens physiques\u000A(concerts, livres…)`}
              </CreditGauge>
            </div>
          </div>
          <div className="rc-read-more">
            <button
              className={`rc-read-more-button ${
                isReadMoreVisible ? 'rc-read-more-drop-down' : 'rc-read-more-drop-down-flipped'
              }`}
              onClick={this.handleToggleReadMore}
              type="button"
            >
              {`Pourquoi les biens numériques sont-ils limités${NON_BREAKING_SPACE}?`}
            </button>
            {isReadMoreVisible && (
              <p className="rc-read-more-content">
                {`Le but du pass Culture est de renforcer tes pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place
                pour favoriser la diversification des pratiques culturelles.`}
              </p>
            )}
          </div>
        </div>
      </section>
    )
  }
}

DepositVersion2.propTypes = {
  user: PropTypes.shape(User).isRequired,
}

export default DepositVersion2
