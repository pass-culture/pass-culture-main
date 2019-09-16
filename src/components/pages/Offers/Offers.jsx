import { Icon, resolveIsNew, showNotification } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Component } from 'react'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'
import { assignData } from 'fetch-normalize-data'

import HeroSection from '../../layout/HeroSection/HeroSection'
import Spinner from '../../layout/Spinner'
import Main from '../../layout/Main'
import { offerNormalizer } from '../../../utils/normalizers'
import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'
import OfferItemContainer from './OfferItem/OfferItemContainer'

class Offers extends Component {
  constructor(props) {
    super(props)

    const { dispatch } = props

    this.state = {
      hasMore: false,
      isLoading: false,
    }

    dispatch(assignData({ offers: [] }))
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
    const { location, offers } = this.props
    const numberOfOffersPerLoad = 10
    const offersHasBeenLoaded = offers.length > prevProps.offers.length


    if (offersHasBeenLoaded) {
      this.scrollerIsNotLoading()

      const allOffersLoaded = offers.length !== prevProps.offers.length + numberOfOffersPerLoad
      if (allOffersLoaded) {
        this.noMoreDataToLoad()
      }
    }

    const { hasMore } = this.state

    if (location.search !== prevProps.location.search && hasMore) {
      this.handleRequestData()
    }
  }

  scrollerIsNotLoading = () => {
    this.setState({ isLoading: false })
  }

  noMoreDataToLoad = () => {
    this.setState({ hasMore: false })
  }

  handleRequestData = () => {
    const { comparedTo, dispatch, query, types } = this.props

    types.length === 0 && dispatch(requestData({ apiPath: '/types' }))

    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/offers?${apiParamsString}`

    this.setState({ isLoading: true, hasMore: true }, () => {
      dispatch(
        requestData({
          apiPath,
          handleFail: () => {
            this.setState({
              hasMore: false,
              isLoading: false,
            })
          },
          handleSuccess: () => {},
          normalizer: offerNormalizer,
          resolve: datum => resolveIsNew(datum, 'dateCreated', comparedTo),
        })
      )
    })
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { dispatch, query } = this.props
    const value = event.target.elements.search.value

    query.change({
      [mapApiToBrowser.keywords]: value === '' ? null : value,
      page: null,
    })

    dispatch(assignData({ offers: [] }))
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
        handleSuccess: this.handleSubmitRequestSuccess('Toutes les offres de ce lieu ont été désactivées avec succès')
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
        handleSuccess: this.handleSubmitRequestSuccess('Toutes les offres de ce lieu ont été activées avec succès')
      })
    )
  }

  handleOnClick = () => {
    // TODO
    // query.change({ })}
  }

  handleOnChange = () => {
    // TODO pagination.orderBy
    // query.change({})
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
                &nbsp;
                &nbsp;
                <Icon svg="ico-filter" />
              </button>
            </p>
          </div>
        </form>

        <ul className="section">
          { offerer &&
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
          }
          { venue &&
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
          }
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

          {
            offers && venue && (
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
            )
          }

          <LoadingInfiniteScroll
            className="offers-list main-list"
            element="ul"
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
        </div>
      </Main>
    )
  }
}

Offers.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default Offers
