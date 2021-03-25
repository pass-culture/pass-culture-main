import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
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
    const { domainsCredit } = user

    const depositVersion = user.deposit_version

    return (
      <section className="pf-section">
        <div className="rc-informations-container">
          <div className="rc-gauges-container">
            <div className="rc-gauges-title">
              {`Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`}
            </div>
            <div className="rc-gauges">
              {domainsCredit.digital && (
                <CreditGauge
                  creditLimit={domainsCredit.digital.initial}
                  extraClassName="gauge-digital"
                  picto="picto-digital-good"
                  remainingCredit={domainsCredit.digital.remaining}
                >
                  {`en offres\u000Anumériques\u000A(streaming…)`}
                </CreditGauge>
              )}
              {domainsCredit.physical && (
                <CreditGauge
                  creditLimit={domainsCredit.physical.initial}
                  extraClassName="gauge-physical"
                  picto="picto-physical-good"
                  remainingCredit={domainsCredit.physical.remaining}
                >
                  {`en offres\u000Aphysiques\u000A(livres…)`}
                </CreditGauge>
              )}
              <CreditGauge
                creditLimit={domainsCredit.all.initial}
                extraClassName="gauge-total"
                picto={depositVersion === 1 ? 'picto-ticket' : 'picto-all-goods'}
                remainingCredit={domainsCredit.all.remaining}
              >
                {depositVersion === 1
                  ? 'en sorties\u000A(spectacles…)'
                  : 'en sorties et\u000Abiens physiques\u000A(concerts, livres…)'}
              </CreditGauge>
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
