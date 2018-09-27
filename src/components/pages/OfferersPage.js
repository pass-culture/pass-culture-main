import {
  Icon,
  InfiniteScroller,
  requestData,
  withLogin,
  withPagination,
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
import { mapApiToWindow, windowToApiQuery } from '../../utils/pagination'

class OfferersPage extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const { dispatch, pagination } = this.props
    const { apiQueryString, page, goToNextPage } = pagination

    dispatch(
      requestData('GET', `offerers?page=${page}&${apiQueryString}`, {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          goToNextPage()
        },
        handleFail,
        normalizer: offererNormalizer,
      })
    )
  }

  onSubmit = event => {
    const { apiQuery, handleQueryQueryChange } = this.props

    event.preventDefault()

    const value = event.target.elements.search.value

    if (!value || apiQuery.search === value) return

    handleQueryQueryChange({ [mapApiToWindow.search]: value })
  }

  render() {
    const { apiQuery, offerers } = this.props

    const { search } = apiQuery || {}

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

        <form className="section" onSubmit={this.onSubmit}>
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
                &nbsp;
                <Icon svg="ico-filter" />
                &nbsp;
              </button>
            </p>
          </div>
        </form>

        <InfiniteScroller
          className="main-list offerers-list"
          handleLoadMore={this.handleDataRequest}>
          {offerers.map(o => (
            <OffererItem key={o.id} offerer={o} />
          ))}
        </InfiniteScroller>
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  return {
    offerers: offerersSelector(state),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withPagination({
    dataKey: 'offerers',
    windowToApiQuery,
  }),
  connect(mapStateToProps)
)(OfferersPage)
