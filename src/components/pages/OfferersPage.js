import {
  InfiniteScroller,
  requestData,
  withLogin,
  withSearch,
} from 'pass-culture-shared'
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
    const { dispatch, goToNextSearchPage, querySearch } = this.props

    dispatch(
      requestData('GET', `offerers?${querySearch}`, {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          goToNextSearchPage()
        },
        handleFail,
        normalizer: offererNormalizer,
      })
    )
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

        <InfiniteScroller
          className="main-list offerers-list"
          handleLoadMore={this.handleDataRequest}>
          {offerers.map(o => <OffererItem key={o.id} offerer={o} />)}
        </InfiniteScroller>
      </Main>
    )
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withSearch({
    dataKey: 'offerers',
    defaultQueryParams: {
      search: undefined,
      order_by: `createdAt+desc`,
    },
  }),
  connect((state, ownProps) => ({
    offerers: offerersSelector(state),
  }))
)(OfferersPage)
