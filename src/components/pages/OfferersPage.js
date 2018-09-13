import { requestData, withLogin } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import HeroSection from '../layout/HeroSection'
import Main from '../layout/Main'
import OffererItem from '../items/OffererItem'
import offerersSelector from '../../selectors/offerers'
import { offererNormalizer } from '../../utils/normalizers'

class OfferersPage extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const { requestData } = this.props
    requestData('GET', 'offerers', {
      handleSuccess,
      handleFail,
      normalizer: offererNormalizer,
    })
  }

  render() {
    const { offerers } = this.props
    return (
      <Main name="offerers" handleDataRequest={this.handleDataRequest}>
        <HeroSection title="Vos structures">
          <p className="subtitle">
            Retrouvez ici la ou les structures dont vous gérez les offres Pass
            Culture.
          </p>
          <NavLink
            to={`/structures/nouveau`}
            className="button is-primary is-outlined">
            + Rattacher une structure supplémentaire
          </NavLink>
        </HeroSection>

        <ul className="main-list offerers-list">
          {offerers.map(o => <OffererItem key={o.id} offerer={o} />)}
        </ul>
      </Main>
    )
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(
    (state, ownProps) => ({
      offerers: offerersSelector(state),
    }),
    {
      requestData,
    }
  )
)(OfferersPage)
