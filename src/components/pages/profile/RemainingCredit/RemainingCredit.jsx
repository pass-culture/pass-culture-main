import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import { getRemainingCreditForGivenCreditLimit } from '../domain/getRemainingCreditForGivenCreditLimit'
import CreditGauge from './CreditGauge/CreditGauge'
import User from '../ValueObjects/User'

class RemainingCredit extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isReadMoreVisible: false,
    }
  }

  handleToggleReadMore = () => {
    this.setState(previousState => ({ isReadMoreVisible: !previousState.isReadMoreVisible }))
  }

  renderDigitalGauge = (depositVersion, expenses, walletBalance) => {
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
      <CreditGauge
        extraClassName="gauge-digital"
        picto="picto-digital-good"
        {...digitalGaugeProperties}
      >
        {`en offres\u000Anumériques\u000A(streaming…)`}
      </CreditGauge>
    )
  }

  renderTotalGauge = (depositVersion, expenses, walletBalance) => {
    let initialDeposit = 0
    if (expenses.length) {
      const all = expenses.find(expense => expense.domain === 'all')
      initialDeposit = all.limit
    }

    const totalGaugeProperties = {
      creditLimit: initialDeposit,
      remainingCredit: walletBalance,
    }

    const gaugeDescription =
      depositVersion === 1
        ? 'en sorties\u000A(spectacles…)'
        : 'en sorties et\u000Abiens physiques\u000A(concerts, livres…)'
    const picto = depositVersion === 1 ? 'picto-ticket' : 'picto-all-goods'

    return (
      <CreditGauge
        extraClassName="gauge-total"
        picto={picto}
        {...totalGaugeProperties}
      >
        {gaugeDescription}
      </CreditGauge>
    )
  }

  renderReadMoreSection = depositVersion => {
    const { isReadMoreVisible } = this.state
    const readMoreTitle =
      depositVersion === 1
        ? `Pourquoi les biens physiques et numériques sont-ils limités${NON_BREAKING_SPACE}?`
        : `Pourquoi les biens numériques sont-ils limités${NON_BREAKING_SPACE}?`

    const readMoreContent =
      depositVersion === 1
        ? `Le but du pass Culture est de renforcer tes pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place
                pour favoriser la diversification des pratiques culturelles.`
        : `Le but du pass Culture est de renforcer tes pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ce plafond a été mis en place
                pour favoriser la diversification des pratiques culturelles.`

    return (
      <div className="rc-read-more">
        <button
          className={`rc-read-more-button ${
            isReadMoreVisible ? 'rc-read-more-drop-down' : 'rc-read-more-drop-down-flipped'
          }`}
          onClick={this.handleToggleReadMore}
          type="button"
        >
          {readMoreTitle}
        </button>
        {isReadMoreVisible && (
          <p className="rc-read-more-content">
            {readMoreContent}
          </p>
        )}
      </div>
    )
  }

  render() {
    const { user } = this.props
    const { expenses, wallet_balance: walletBalance } = user

    const depositVersion = user.deposit_version

    let physicalCreditLimit = 0
    let physicalRemainingCredit = 0
    const VERSION_1 = 1
    if (expenses.length && user.deposit_version === VERSION_1) {
      const physical = expenses.find(expense => expense.domain === 'physical')
      physicalCreditLimit = physical.limit
      physicalRemainingCredit = getRemainingCreditForGivenCreditLimit(walletBalance)(physical)
    }

    const physicalGaugeProperties = {
      creditLimit: physicalCreditLimit,
      remainingCredit: physicalRemainingCredit,
    }

    return (
      <section className="pf-section">
        <div className="rc-informations-container">
          <div className="rc-gauges-container">
            <div className="rc-gauges-title">
              {`Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`}
            </div>
            <div className="rc-gauges">
              {this.renderDigitalGauge(depositVersion, expenses, walletBalance)}
              {depositVersion === 1 && (
                <CreditGauge
                  extraClassName="gauge-physical"
                  picto="picto-physical-good"
                  {...physicalGaugeProperties}
                >
                  {`en offres\u000Aphysiques\u000A(livres…)`}
                </CreditGauge>
              )}
              {this.renderTotalGauge(depositVersion, expenses, walletBalance)}
            </div>
          </div>
          {this.renderReadMoreSection(depositVersion)}
        </div>
      </section>
    )
  }
}

RemainingCredit.propTypes = {
  user: PropTypes.shape(User).isRequired,
}

export default RemainingCredit
