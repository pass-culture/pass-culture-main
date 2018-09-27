import get from 'lodash.get'
import {
  Icon,
  InfiniteScroller,
  lastTrackerMoment,
  requestData,
  resolveIsNew,
  withLogin,
  withPagination,
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
import { mapApiToWindow, windowToApiQuery } from '../../utils/pagination'

class OffersPage extends Component {
  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { comparedTo, dispatch, pagination, search, types } = this.props

    const { apiQueryString, goToNextPage, page } = pagination

    if (page !== 1 && search.page && page === Number(search.page)) {
      return
    }

    const path = `offers?page=${page}&${apiQueryString}`

    dispatch(
      requestData('GET', path, {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          goToNextPage()
        },
        handleFail,
        normalizer: offerNormalizer,
        resolve: datum => resolveIsNew(datum, 'dateCreated', comparedTo),
      })
    )
    types.length === 0 && dispatch(requestData('GET', 'types'))
  }

  onSubmit = event => {
    const { pagination } = this.props

    event.preventDefault()

    const value = event.target.elements.search.value

    if (!value || pagination.apiQuery.search === value) return

    pagination.change({ [mapApiToWindow.search]: value })
  }

  render() {
    const { offers, offerer, pagination, venue, user } = this.props

    const { venueId, search, order_by, offererId } = pagination.apiQuery || {}

    let createOfferTo = `/offres/nouveau`
    if (venueId) {
      createOfferTo = `${createOfferTo}?lieu=${venueId}`
    } else if (offererId) {
      createOfferTo = `${createOfferTo}?structure=${offererId}`
    }

    const [orderBy, orderDirection] = (order_by || '').split('+')

    return (
      <Main name="offers" handleDataRequest={this.handleDataRequest}>
        <HeroSection title="Vos offres">
          {!get(user, 'isAdmin') && (
            <NavLink to={createOfferTo} className="cta button is-primary">
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>Créer une offre</span>
            </NavLink>
          )}
        </HeroSection>
        <form className="section" onSubmit={this.onSubmit}>
          <label className="label">Rechercher une offre :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                id="search"
                className="input"
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
                onClick={() => pagination.change({ offererId: null })}
              />
            </li>
          ) : (
            venue && (
              <li className="tag is-rounded is-medium">
                Lieu :
                <span className="has-text-weight-semibold">{venue.name}</span>
                <button
                  className="delete is-small"
                  onClick={() => pagination.change({ venueId: null })}
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
                    onChange={pagination.orderBy}
                    className=""
                    value={orderBy}>
                    <option value="sold">Offres écoulées</option>
                    <option value="createdAt">Date de création</option>
                  </select>
                </span>
              </div>
              <div>
                <button
                  onClick={pagination.reverseOrder}
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
                handleLoadMore={(handleSuccess, handleFail) => {
                  this.handleDataRequest(handleSuccess, handleFail)
                  const { history, location, pagination } = this.props
                  const { windowQueryString, page } = pagination
                  history.push(
                    `${location.pathname}?page=${page}&${windowQueryString}`
                  )
                }}>
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
  const { offererId, venueId } = ownProps.pagination.apiQuery
  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    offers: offersSelector(state, offererId, venueId),
    offerer: offererSelector(state, offererId),
    user: state.user,
    types: state.data.types,
    venue: venueSelector(state, venueId),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  withPagination({
    dataKey: 'offers',
    windowToApiQuery,
  }),
  connect(mapStateToProps)
)(OffersPage)
