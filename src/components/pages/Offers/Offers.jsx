import { Icon, resolveIsNew, showNotification } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Component } from 'react'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import HeroSection from '../../layout/HeroSection/HeroSection'
import Spinner from '../../layout/Spinner'
import Main from '../../layout/Main'

import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'
import OfferItemContainer from './OfferItem/OfferItemContainer'
import selectOffersByOffererIdAndVenueId from '../../../selectors/selectOffersByOffererIdAndVenueId'

class Offers extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasMore: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const { query } = this.props
    const queryParams = query.parse()

    if (queryParams.page) {
      query.change({ page: null })
    } else {
      this.handleRequestData()
    }
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props

    if (location.search !== prevProps.location.search) {
      this.handleRequestData()
    }
  }

  handleRequestData = () => {
    const { comparedTo, dispatch, loadOffers, query, types } = this.props

    types.length === 0 && dispatch(requestData({ apiPath: '/types' }))

    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/offers?${apiParamsString}`

    const handleSuccess = (state, action) => {
      const { payload } = action
      const { headers } = payload
      const apiQueryParams = translateQueryParamsToApiParams(queryParams)
      const { offererId, venueId } = apiQueryParams
      const nextOffers = selectOffersByOffererIdAndVenueId(state, offererId, venueId)
      const totalOffersCount = parseInt(headers['total-data-count'], 10)
      const currentOffersCount = nextOffers.length

      this.setState({
        hasMore: currentOffersCount < totalOffersCount,
        isLoading: false,
      })
    }

    const handleFail = () =>
      this.setState({
        isLoading: false,
      })

    const resolve = datum => resolveIsNew(datum, 'dateCreated', comparedTo)

    this.setState({ hasMore: true, isLoading: true }, () =>
      loadOffers({ apiPath, handleSuccess, handleFail, resolve })
    )
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { query, resetLoadedOffers } = this.props
    const queryParams = query.parse()
    const value = event.target.elements.search.value

    query.change({
      [mapApiToBrowser.keywords]: value === '' ? null : value,
      page: null,
    })

    if (queryParams[mapApiToBrowser.keywords] !== value) resetLoadedOffers()
  }

  handleSubmitRequestSuccess = notificationMessage => {
    const { dispatch } = this.props
    dispatch(
      showNotification({
        text: notificationMessage,
        type: 'success',
      })
    )
  }

  handleOnVenueClick = query => () => {
    query.change({
      [mapApiToBrowser.venueId]: null,
      page: null,
    })
  }

  handleOnOffererClick = query => () => {
    query.change({
      [mapApiToBrowser.offererId]: null,
      page: null,
    })
  }

  handleOnDeactivateAllVenueOffersClick = () => {
    const { dispatch, venue } = this.props
    dispatch(
      requestData({
        apiPath: `/venues/${venue.id}/offers/deactivate`,
        method: 'PUT',
        stateKey: 'offers',
        handleSuccess: this.handleSubmitRequestSuccess(
          'Toutes les offres de ce lieu ont été désactivées avec succès'
        ),
      })
    )
  }

  handleOnActivateAllVenueOffersClick = () => {
    const { dispatch, venue } = this.props
    dispatch(
      requestData({
        apiPath: `/venues/${venue.id}/offers/activate`,
        method: 'PUT',
        stateKey: 'offers',
        handleSuccess: this.handleSubmitRequestSuccess(
          'Toutes les offres de ce lieu ont été activées avec succès'
        ),
      })
    )
  }

  onPageChange = page => {
    const { query } = this.props
    query.change({ page }, { historyMethod: 'replace' })
  }

  onPageReset = () => {
    const { query } = this.props
    query.change({ page: null })
  }

  render() {
    const { currentUser, offers, offerer, query, venue } = this.props

    const { isAdmin } = currentUser || {}
    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const { keywords, venueId, offererId, orderBy } = apiParams
    const { hasMore, isLoading } = this.state

    let createOfferTo = `/offres/creation`
    if (venueId) {
      createOfferTo = `${createOfferTo}?${mapApiToBrowser.venueId}=${venueId}`
    } else if (offererId) {
      createOfferTo = `${createOfferTo}?${mapApiToBrowser.offererId}=${offererId}`
    }

    const [orderName, orderDirection] = (orderBy || '').split('+')

    return (
      <Main
        id="offers"
        name="offers"
      >
        <HeroSection title="Vos offres">
          {!isAdmin && (
            <NavLink
              className="cta button is-primary"
              to={createOfferTo}
            >
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>
                {'Créer une offre'}
              </span>
            </NavLink>
          )}
        </HeroSection>
        <form
          className="section"
          onSubmit={this.handleOnSubmit}
        >
          <label className="label">
            {'Rechercher une offre :'}
          </label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                className="input"
                defaultValue={keywords}
                id="search"
                placeholder="Saisissez un ou plusieurs mots complets"
                type="text"
              />
            </p>
            <p className="control">
              <button
                className="button is-primary is-outlined"
                id="search-button"
                type="submit"
              >
                {'OK'}
              </button>
              <button
                className="button is-secondary"
                disabled
                type="button"
              >
                &nbsp; &nbsp;
                <Icon svg="ico-filter" />
              </button>
            </p>
          </div>
        </form>

        <ul className="section">
          {offerer && (
            <button
              className="offerer-filter tag is-rounded is-medium"
              onClick={this.handleOnOffererClick(query)}
              type="button"
            >
              {'Structure :'}
              <span className="name">
                &nbsp;
                {offerer.name}
              </span>
              <Icon svg="ico-close-r" />
            </button>
          )}
          {venue && (
            <button
              className="venue-filter tag is-rounded is-medium"
              onClick={this.handleOnVenueClick(query)}
              type="button"
            >
              {'Lieu : '}
              <span className="name">
                {venue.name}
              </span>
              <Icon svg="ico-close-r" />
            </button>
          )}
        </ul>
        <div className="section">
          {false && (
            <div className="list-header">
              <div>
                <div className="recently-added" />
                {'Ajouté récemment'}
              </div>
              <div>
                {'Trier par: '}
                <span className="select is-rounded is-small">
                  <select
                    onBlur={this.handleOnChange}
                    value={orderName}
                  >
                    <option value="sold">
                      {'Offres écoulées'}
                    </option>
                    <option value="createdAt">
                      {'Date de création'}
                    </option>
                  </select>
                </span>
              </div>
              <div>
                <button
                  className="button is-secondary"
                  onClick={this.handleOnClick}
                  type="button"
                >
                  <Icon
                    svg={orderDirection === 'asc' ? 'ico-sort-ascending' : 'ico-sort-descending'}
                  />
                </button>
              </div>
            </div>
          )}

          {offers && venue && (
            <div className="offers-list-actions">
              <button
                className="button deactivate is-secondary is-small"
                onClick={this.handleOnDeactivateAllVenueOffersClick}
                type="button"
              >
                {'Désactiver toutes les offres'}
              </button>

              <button
                className="button activate is-secondary is-small"
                onClick={this.handleOnActivateAllVenueOffersClick}
                type="button"
              >
                {'Activer toutes les offres'}
              </button>
            </div>
          )}

          <LoadingInfiniteScroll
            className="offers-list main-list"
            element="ul"
            handlePageChange={this.onPageChange}
            handlePageReset={this.onPageReset}
            hasMore={hasMore}
            isLoading={isLoading}
            loader={<Spinner key="spinner" />}
          >
            {offers.map(offer => (
              <OfferItemContainer
                key={offer.id}
                offer={offer}
              />
            ))}
          </LoadingInfiniteScroll>
          {hasMore === false && 'Fin des résultats'}
        </div>
      </Main>
    )
  }
}

Offers.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  resetLoadedOffers: PropTypes.func.isRequired,
}

export default Offers
