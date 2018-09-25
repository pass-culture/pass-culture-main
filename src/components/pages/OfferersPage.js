import {
  Icon,
  InfiniteScroller,
  requestData,
  searchSelector,
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
    const { handleSearchChange, queryParams, offerers } = this.props

    const { search, order_by } = queryParams || {}

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

        <form className="section" onSubmit={handleSearchChange}>
          <label className="label">Rechercher une structure :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                id="search"
                className="input search-input"
                placeholder="Saisissez une recherche"
                type="text"
                defaultValue={search}
              />
            </p>
            <p className="control">
              <button type="submit" className="button is-primary is-outlined">
                OK
              </button>{' '}
              <button className="button is-secondary" disabled>
                &nbsp;<Icon svg="ico-filter" />&nbsp;
              </button>
            </p>
          </div>
        </form>

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
    queryParams: searchSelector(state, ownProps.location.search),
  }))
)(OfferersPage)
