import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { computeEndValidityDate } from '../../../../utils/date/date'
import formatDecimals from '../../../../utils/numbers/formatDecimals'
import Icon from '../../../layout/Icon/Icon'
import getRemainingCreditForGivenCreditLimit from '../utils/utils'
import CreditGauge from './CreditGauge/CreditGauge'

const NON_BREAKING_SPACE = '\u00A0'

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
    const { currentUser } = this.props
    const { isReadMoreVisible } = this.state
    const {
      expenses,
      wallet_date_created: walletDateCreated,
      wallet_balance: walletBalance,
    } = currentUser
    const formattedWalletBalance = formatDecimals(walletBalance)
    const { digital, physical, all } = expenses
    const digitalCreditLimit = digital.max
    const physicalCreditLimit = physical.max
    const initialDeposit = all.max
    const digitalRemainingCredit = getRemainingCreditForGivenCreditLimit(walletBalance)(digital)
    const physicalRemainingCredit = getRemainingCreditForGivenCreditLimit(walletBalance)(physical)
    let endValidityDate = null
    if (walletDateCreated) {
      endValidityDate = computeEndValidityDate(new Date(walletDateCreated))
    }

    return (
      <div>
        <div className="rc-title-container">
          <h2 className="rc-title">
            {'Crédit restant'}
          </h2>
        </div>

        <div className="rc-informations-container">
          <div className="rc-header">
            <Icon svg="picto-money" />
            <div>
              <div className="rc-header-title">
                {'Mon crédit'}
              </div>
              <p>
                {`${formattedWalletBalance}${NON_BREAKING_SPACE}€`}
              </p>
            </div>
          </div>
          <div className="rc-gauges-container">
            <div className="rc-gauges-title">
              {`Vous pouvez encore dépenser jusqu’à${NON_BREAKING_SPACE}:`}
            </div>
            <div className="rc-gauges">
              <CreditGauge
                creditLimit={digitalCreditLimit}
                detailsText="en offres numériques (streaming…)"
                extraClassName="gauge-digital"
                picto="picto-digital-good"
                remainingCredit={digitalRemainingCredit}
              />
              <CreditGauge
                creditLimit={physicalCreditLimit}
                detailsText="en offres physiques (livres…)"
                extraClassName="gauge-physical"
                picto="picto-physical-good"
                remainingCredit={physicalRemainingCredit}
              />
              <CreditGauge
                creditLimit={initialDeposit}
                detailsText="en autres offres (concerts…)"
                extraClassName="gauge-total"
                picto="picto-ticket"
                remainingCredit={walletBalance}
              />
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
                {`Le but du pass Culture est de renforcer vos pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place
                pour favoriser la diversification des pratiques culturelles.`}
              </p>
            )}
          </div>
        </div>
        {endValidityDate && (
          <div>
            <p className="rc-end-validity-date">
              {`Votre crédit est valable jusqu’au ${endValidityDate}.`}
            </p>
          </div>
        )}
      </div>
    )
  }
}

RemainingCredit.propTypes = {
  currentUser: PropTypes.shape().isRequired,
}

export default RemainingCredit
