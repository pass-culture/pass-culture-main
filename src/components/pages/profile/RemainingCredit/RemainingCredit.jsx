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

  render() {
    const { user } = this.props
    const { isReadMoreVisible } = this.state
    const { expenses, wallet_balance: walletBalance } = user
    const { digital, physical, all } = expenses
    const digitalCreditLimit = digital.max
    const physicalCreditLimit = physical.max
    const initialDeposit = all.max
    const digitalRemainingCredit = getRemainingCreditForGivenCreditLimit(walletBalance)(digital)
    const physicalRemainingCredit = getRemainingCreditForGivenCreditLimit(walletBalance)(physical)

    return (
      <section className="profile-section">
        <div className="rc-informations-container">
          <div className="rc-gauges-container">
            <div className="rc-gauges-title">
              {`Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`}
            </div>
            <div className="rc-gauges">
              <CreditGauge
                creditLimit={digitalCreditLimit}
                extraClassName="gauge-digital"
                picto="picto-digital-good"
                remainingCredit={digitalRemainingCredit}
              >
                {`en offres\u000Anumériques\u000A(streaming…)`}
              </CreditGauge>
              <CreditGauge
                creditLimit={physicalCreditLimit}
                extraClassName="gauge-physical"
                picto="picto-physical-good"
                remainingCredit={physicalRemainingCredit}
              >
                {`en offres\u000Aphysiques\u000A(livres…)`}
              </CreditGauge>
              <CreditGauge
                creditLimit={initialDeposit}
                extraClassName="gauge-total"
                picto="picto-ticket"
                remainingCredit={walletBalance}
              >
                {`en sorties\u000A(spectacles…)`}
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
              {`Pourquoi les biens physiques et numériques sont-ils limités${NON_BREAKING_SPACE}?`}
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

RemainingCredit.propTypes = {
  user: PropTypes.instanceOf(User).isRequired,
}

export default RemainingCredit
