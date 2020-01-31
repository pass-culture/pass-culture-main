import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import getAvailableBalanceByType from '../utils/utils'
import { formatEndValidityDate } from '../../../../utils/date/date'
import CreditGauge from './CreditGauge/CreditGauge'
import Icon from '../../../layout/Icon/Icon'
import formatDecimals from '../../../../utils/numbers/formatDecimals'

class RemainingCredit extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      readMoreIsVisible: false
    }
  }

  handleToggleReadMore = () => {
    this.setState(previousState => ({ readMoreIsVisible: !previousState.readMoreIsVisible }))
  }

  render() {
    const { currentUser } = this.props
    const { readMoreIsVisible } = this.state
    const { expenses, wallet_date_created, wallet_balance: walletBalance } = currentUser || {}
    const formattedWalletBalance = formatDecimals(walletBalance)
    const { digital, physical, all } = expenses
    const maxAmountDigital = digital.max
    const maxAmountPhysical = physical.max
    const maxAmountAll = all.max
    const [digitalAvailable, physicalAvailable] = [digital, physical].map(
      getAvailableBalanceByType(walletBalance)
    )
    let endValidityDate = null
    if (wallet_date_created) {
      endValidityDate = formatEndValidityDate(new Date(wallet_date_created))
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
              <h3>
                {'Mon crédit'}
              </h3>
              <p>
                {formattedWalletBalance}
                &nbsp;
                {'€'}
              </p>
            </div>
          </div>
          <div className="rc-gauges-container">
            <div className="rc-gauges-title">
              {'Vous pouvez encore dépenser jusqu’à'}
              &nbsp;
              {':'}
            </div>
            <div className="rc-gauges">
              <CreditGauge
                className="gauge-digital"
                currentAmount={digitalAvailable}
                detailsText="en offres numériques (streaming, …)"
                maxAmount={maxAmountDigital}
                picto="picto-digital-good"
              />
              <CreditGauge
                className="gauge-physical"
                currentAmount={physicalAvailable}
                detailsText="en offres physiques (livres, …)"
                maxAmount={maxAmountPhysical}
                picto="picto-physical-good"
              />
              <CreditGauge
                className="gauge-total"
                currentAmount={walletBalance}
                detailsText="en autres offres (concerts, …)"
                maxAmount={maxAmountAll}
                picto="picto-ticket"
              />
            </div>
          </div>
          <div className="rc-read-more">
            <button
              className="rc-read-more-button"
              onClick={this.handleToggleReadMore}
              type="button"
            >
              <div className="rc-read-more-title">
                {'Pourquoi les biens physiques et numériques sont-ils limités'}
                &nbsp;
                {'?'}
              </div>
              <Icon
                className={`rc-read-more-arrow ${
                  readMoreIsVisible ? 'rc-read-more-arrow-is-flipped' : ''
                }`}
                svg="picto-drop-down"
              />
            </button>
            <p
              className={`rc-read-more-content ${
                readMoreIsVisible ? 'rc-read-more-content-is-visible' : ''
              }`}
            >
              {'Le but du pass Culture est de renforcer vos pratiques culturelles, '}
              {'mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place '}
              {'pour favoriser la diversification des pratiques culturelles.'}
            </p>
          </div>
        </div>
        <div>
          {endValidityDate && (
            <p className="rc-end-validity-date">
              {`Votre crédit est valable jusqu’au ${endValidityDate}.`}
            </p>
          )}
        </div>
      </div>
    )
  }
}

RemainingCredit.propTypes = {
  currentUser: PropTypes.shape().isRequired
}

export default RemainingCredit
