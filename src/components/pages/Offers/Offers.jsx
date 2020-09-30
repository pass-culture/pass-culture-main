import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'
import { Link } from 'react-router-dom'

import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'
import TextInput from '../../layout/inputs/TextInput/TextInput'
import Main from '../../layout/Main'

import Titles from '../../layout/Titles/Titles'
import OfferItemContainer from './OfferItem/OfferItemContainer'
import Spinner from '../../layout/Spinner'

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

    const { name: nameKeywords, page, venueId } = translateQueryParamsToApiParams(
      props.query.parse()
    )

    this.state = {
      isLoading: false,
      nameSearchValue: nameKeywords || '',
      page: page || 1,
      pageCount: null,
      venueId: venueId,
    }
  }

  componentDidMount() {
    this.getPaginatedOffersWithFilters()
  }

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (notification && notification.tag === 'offers-activation') {
      closeNotification()
    }
  }

  updateUrlMatchingState = () => {
    const { query } = this.props
    const { page, nameSearchValue, venueId } = this.state

    query.change({
      page: page,
      [mapApiToBrowser.name]: nameSearchValue === '' ? null : nameSearchValue,
      [mapApiToBrowser.venueId]: venueId ? venueId : null,
    })
  }

  getPaginatedOffersWithFilters = () => {
    const { loadTypes, loadOffers, types } = this.props
    const { nameSearchValue, venueId, page } = this.state
    types.length === 0 && loadTypes()

    const handleSuccess = (page, pageCount) => {
      this.setState(
        {
          isLoading: false,
          page,
          pageCount,
        },
        () => {
          this.updateUrlMatchingState()
        }
      )
    }

    const handleFail = () =>
      this.setState({
        isLoading: false,
      })

    this.setState({ isLoading: true }, () => {
      loadOffers({ nameSearchValue, venueId, page }, handleSuccess, handleFail)
    })
  }

  handleOnSubmit = event => {
    event.preventDefault()

    this.setState(
      {
        page: 1,
      },
      () => {
        this.getPaginatedOffersWithFilters()
      }
    )
  }

  handleOnVenueClick = () => {
    this.setState(
      {
        venueId: undefined,
        page: 1,
      },
      () => {
        this.getPaginatedOffersWithFilters()
      }
    )
  }

  storeNameSearchValue = event => {
    this.setState({ nameSearchValue: event.target.value })
  }

  onPreviousPageClick = () => {
    const { page } = this.state
    this.setState({ page: page - 1 }, () => {
      this.getPaginatedOffersWithFilters()
    })
  }

  onNextPageClick = () => {
    const { page } = this.state
    this.setState({ page: page + 1 }, () => {
      this.getPaginatedOffersWithFilters()
    })
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
    const { nameSearchValue, page, pageCount, isLoading } = this.state
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
              onClick={this.handleOnVenueClick}
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
          {isLoading && <Spinner />}
          {offers.length > 0 && !isLoading && (
            <Fragment>
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
                <tbody className="offers-list">
                  {offers.map(offer => (
                    <OfferItemContainer
                      key={offer.id}
                      offer={offer}
                    />
                  ))}
                </tbody>
              </table>
              <div className="pagination">
                <button
                  disabled={page === 1}
                  onClick={this.onPreviousPageClick}
                  type="button"
                >
                  <Icon
                    alt="Aller à la page précédente"
                    svg="ico-left-arrow"
                  />
                </button>
                <span>
                  {`Page ${page}/${pageCount}`}
                </span>
                <button
                  disabled={page === pageCount}
                  onClick={this.onNextPageClick}
                  type="button"
                >
                  <Icon
                    alt="Aller à la page suivante"
                    svg="ico-right-arrow"
                  />
                </button>
              </div>
            </Fragment>
          )}
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
  venue: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }),
}

export default Offers
