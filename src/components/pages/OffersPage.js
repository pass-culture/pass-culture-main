import {
  Icon,
  InfiniteScroller,
  lastTrackerMoment,
  requestData,
  resolveIsNew,
  withSearch,
  withLogin,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import HeroSection from '../layout/HeroSection'
import OfferItem from '../items/OfferItem'
import Main from '../layout/Main'
import offersSelector from '../../selectors/offers'
import offererSelector from '../../selectors/offerer'
import venueSelector from '../../selectors/venue'
import { offerNormalizer } from '../../utils/normalizers'
import { queryToApiParams } from '../../utils/search'

class OffersPage extends Component {
  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const {
      comparedTo,
      dispatch,
      goToNextSearchPage,
      querySearch,
      types,
    } = this.props
    dispatch(
      requestData('GET', `offers?${querySearch}`, {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          goToNextSearchPage()
        },
        handleFail,
        normalizer: offerNormalizer,
        resolve: datum => resolveIsNew(datum, 'dateCreated', comparedTo),
      })
    )
    types.length === 0 && dispatch(requestData('GET', 'types'))
  }

  render() {
    const {
      handleOrderByChange,
      handleOrderDirectionChange,
      handleRemoveFilter,
      handleSearchChange,
      offers,
      offerer,
      queryParams,
      venue,
    } = this.props

    const { search, order_by } = queryParams || {}

    const [orderBy, orderDirection] = (order_by || '').split('+')
    return (
      <Main name="offers" handleDataRequest={this.handleDataRequest}>
        <HeroSection title="Vos offres">
          <NavLink to={`/offres/nouveau`} className="cta button is-primary">
            <span className="icon">
              <Icon svg="ico-offres-w" />
            </span>
            <span>Créer une offre</span>
          </NavLink>
        </HeroSection>
        <form className="section" onSubmit={handleSearchChange}>
          <label className="label">Rechercher une offre :</label>
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

        <ul className="section">
          {offerer ? (
            <li className="tag is-rounded is-medium">
              Structure :
              <span className="has-text-weight-semibold"> {offerer.name} </span>
              <button
                className="delete is-small"
                onClick={handleRemoveFilter('offererId')}
              />
            </li>
          ) : (
            venue && (
              <li className="tag is-rounded is-medium">
                Lieu :
                <span className="has-text-weight-semibold">{venue.name}</span>
                <button
                  className="delete is-small"
                  onClick={handleRemoveFilter('venueId')}
                />
              </li>
            )
          )}
        </ul>

        {
          <div className="section">
            <div className="list-header">
              <div>
                <div className="recently-added" />
                Ajouté récemment
              </div>
              <div>
                Trier par:
                <span className="select is-rounded is-small">
                  <select
                    onChange={handleOrderByChange}
                    className=""
                    value={orderBy}>
                    <option value="sold">Offres écoulées</option>
                    <option value="createdAt">Date de création</option>
                  </select>
                </span>
              </div>
              <div>
                <button
                  onClick={handleOrderDirectionChange}
                  className="button is-secondary">
                  <Icon
                    svg={
                      orderDirection === 'asc'
                        ? 'ico-sort-ascending'
                        : 'ico-sort-descending'
                    }
                  />
                </button>
              </div>
            </div>
            {
              <InfiniteScroller
                className="offers-list main-list"
                handleLoadMore={this.handleDataRequest}>
                {offers.map(o => (
                  <OfferItem key={o.id} offer={o} />
                ))}
              </InfiniteScroller>
            }
          </div>
        }
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  const { lieu, structure } = ownProps.queryParams
  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    offers: offersSelector(state, structure, lieu),
    offerer: offererSelector(state, structure),
    user: state.user,
    types: state.data.types,
    venue: venueSelector(state, lieu),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  withSearch({
    queryToApiParams,
    dataKey: 'offers',
    defaultQueryParams: {
      lieu: null,
      search: undefined,
      structure: null,
      order_by: `createdAt+desc`,
    },
  }),
  connect(mapStateToProps)
)(OffersPage)
