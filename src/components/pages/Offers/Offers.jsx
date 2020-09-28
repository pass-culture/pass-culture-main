import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { Link } from 'react-router-dom'

import Titles from '../../layout/Titles/Titles'
import Spinner from '../../layout/Spinner'
import Main from '../../layout/Main'

import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'
import OfferItemContainer from './OfferItem/OfferItemContainer'
import TextInput from '../../layout/inputs/TextInput/TextInput'

export const createLinkToOfferCreation = (venueId, offererId) => {
  let createOfferTo = `/offres/creation`

  if (venueId && offererId) {
    createOfferTo = `${createOfferTo}?${mapApiToBrowser.offererId}=${offererId}&${mapApiToBrowser.venueId}=${venueId}`
  } else if (offererId) {
    createOfferTo = `${createOfferTo}?${mapApiToBrowser.offererId}=${offererId}`
  } else if (venueId) {
    createOfferTo = `${createOfferTo}?${mapApiToBrowser.venueId}=${venueId}`
  }

  return createOfferTo
}

class Offers extends PureComponent {
  constructor(props) {
    super(props)

    const { name: nameKeywords, venueId } = translateQueryParamsToApiParams(props.query.parse())

    this.state = {
      hasMore: false,
      isLoading: false,
      nameSearchValue: nameKeywords || '',
      venueId: venueId,
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

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (notification && notification.tag === 'offers-activation') {
      closeNotification()
    }
  }

  handleRequestData = () => {
    const { loadTypes, loadOffers, query, types } = this.props
    const { nameSearchValue, venueId } = this.state
    const { page } = translateQueryParamsToApiParams(query.parse())

    types.length === 0 && loadTypes()

    const handleSuccess = (page, pageCount) => {
      this.setState({
        hasMore: page < pageCount,
        isLoading: false,
      })
    }

    const handleFail = () =>
      this.setState({
        isLoading: false,
      })

    this.setState({ hasMore: true, isLoading: true }, () =>
      loadOffers({ nameSearchValue, venueId, page }, handleSuccess, handleFail)
    )
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { nameSearchValue } = this.state
    const { query, resetLoadedOffers } = this.props
    const queryParams = query.parse()
    const value = nameSearchValue

    query.change({
      [mapApiToBrowser.name]: value === '' ? null : value,
      page: null,
    })

    if (value && queryParams[mapApiToBrowser.name] !== value) resetLoadedOffers()
  }

  handleOnVenueClick = query => () => {
    query.change({
      [mapApiToBrowser.venueId]: null,
      page: null,
    })
  }

  onPageChange = page => {
    const { query } = this.props
    query.change({ page }, { historyMethod: 'replace' })
  }

  onPageReset = () => {
    const { query } = this.props
    query.change({ page: null })
  }

  storeNameSearchValue = event => {
    this.setState({ nameSearchValue: event.target.value })
  }

  render() {
    const {
      currentUser,
      handleOnDeactivateAllVenueOffersClick,
      handleOnActivateAllVenueOffersClick,
      offers,
      query,
      venue,
    } = this.props

    const { isAdmin } = currentUser || {}
    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const { venueId, offererId } = apiParams
    const { hasMore, isLoading, nameSearchValue } = this.state
    const createOfferTo = createLinkToOfferCreation(venueId, offererId)

    const actionLink = !isAdmin ? (
      <Link
        className="cta button is-primary"
        to={createOfferTo}
      >
        <span className="icon">
          <Icon svg="ico-offres-w" />
        </span>
        <span>
          {'Créer une offre'}
        </span>
      </Link>
    ) : null

    return (
      <Main
        id="offers"
        name="offers"
      >
        <Titles
          action={actionLink}
          title="Offres"
        />
        <form
          className="section"
          onSubmit={this.handleOnSubmit}
        >
          <TextInput
            label="Nom de l’offre"
            name="search"
            onChange={this.storeNameSearchValue}
            placeholder="Rechercher par nom d’offre"
            value={nameSearchValue}
          />
          <div className="search-separator">
            <div className="separator" />
            <button
              className="primary-button"
              type="submit"
            >
              {'Lancer la recherche'}
            </button>
            <div className="separator" />
          </div>
        </form>

        <ul className="section">
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
          {offers && venue && (
            <div className="offers-list-actions">
              <button
                className="button deactivate is-tertiary is-small"
                onClick={handleOnDeactivateAllVenueOffersClick(venue)}
                type="button"
              >
                {'Désactiver toutes les offres'}
              </button>

              <button
                className="button activate is-tertiary is-small"
                onClick={handleOnActivateAllVenueOffersClick(venue)}
                type="button"
              >
                {'Activer toutes les offres'}
              </button>
            </div>
          )}

          {offers.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th />
                  <th />
                  <th>
                    {'Lieu'}
                  </th>
                  <th>
                    {'Stock'}
                  </th>
                  <th>
                    {'Statut'}
                  </th>
                  <th />
                  <th />
                </tr>
              </thead>
              <LoadingInfiniteScroll
                className="offers-list"
                element="tbody"
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
            </table>
          )}
          {hasMore === false && 'Fin des résultats'}
        </div>
      </Main>
    )
  }
}

Offers.defaultProps = {
  venue: undefined,
}

Offers.propTypes = {
  closeNotification: PropTypes.func.isRequired,
  currentUser: PropTypes.shape().isRequired,
  handleOnActivateAllVenueOffersClick: PropTypes.func.isRequired,
  handleOnDeactivateAllVenueOffersClick: PropTypes.func.isRequired,
  loadOffers: PropTypes.func.isRequired,
  loadTypes: PropTypes.func.isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  resetLoadedOffers: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }),
}

export default Offers
