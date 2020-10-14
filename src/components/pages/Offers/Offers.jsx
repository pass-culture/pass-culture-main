import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Link } from 'react-router-dom'

import { fetchAllVenuesByProUser } from '../../../services/venuesService'
import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'
import Select from '../../layout/inputs/Select'
import TextInput from '../../layout/inputs/TextInput/TextInput'
import Main from '../../layout/Main'
import Spinner from '../../layout/Spinner'
import Titles from '../../layout/Titles/Titles'
import formatAndOrderVenues from '../Bookings/BookingsRecapTable/utils/formatAndOrderVenues'
import { ALL_OFFERS, ALL_VENUES, ALL_VENUES_OPTION, DEFAULT_PAGE } from './_constants'
import OfferItemContainer from './OfferItem/OfferItemContainer'

class Offers extends PureComponent {
  constructor(props) {
    super(props)

    const { name: nameKeywords, page, venueId: selectedVenueId } = translateQueryParamsToApiParams(
      props.query.parse()
    )
    this.state = {
      isLoading: false,
      nameSearchValue: nameKeywords || ALL_OFFERS,
      offersCount: 0,
      page: page || DEFAULT_PAGE,
      pageCount: null,
      selectedVenueId: selectedVenueId || ALL_VENUES,
      venueOptions: [],
    }
  }

  componentDidMount() {
    this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
    fetchAllVenuesByProUser().then(venues =>
      this.setState({ venueOptions: formatAndOrderVenues(venues) })
    )
  }

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (notification && notification.tag === 'offers-activation') {
      closeNotification()
    }
  }

  updateUrlMatchingState = () => {
    const { query } = this.props
    const { page, nameSearchValue, selectedVenueId } = this.state

    query.change({
      page: page === DEFAULT_PAGE ? null : page,
      [mapApiToBrowser.name]: nameSearchValue === ALL_OFFERS ? null : nameSearchValue,
      [mapApiToBrowser.venueId]: selectedVenueId === ALL_VENUES ? null : selectedVenueId,
    })
  }

  loadAndUpdateOffers() {
    const { loadOffers } = this.props
    const { nameSearchValue, selectedVenueId, page } = this.state

    loadOffers({ nameSearchValue, selectedVenueId, page })
      .then(({ page, pageCount, offersCount }) => {
        this.setState(
          {
            isLoading: false,
            offersCount,
            page,
            pageCount,
          },
          () => {
            this.updateUrlMatchingState()
          }
        )
      })
      .catch(() => {
        this.setState({
          isLoading: false,
        })
      })
  }

  getPaginatedOffersWithFilters = ({ shouldTriggerSpinner }) => {
    const { loadTypes, types, saveSearchFilters } = this.props
    const { nameSearchValue, selectedVenueId, page } = this.state
    types.length === 0 && loadTypes()
    saveSearchFilters({ name: nameSearchValue, venueId: selectedVenueId, page })

    shouldTriggerSpinner && this.setState({ isLoading: true })

    this.loadAndUpdateOffers()
  }

  handleOnSubmit = event => {
    event.preventDefault()

    this.setState(
      {
        page: DEFAULT_PAGE,
      },
      () => {
        this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
      }
    )
  }

  storeNameSearchValue = event => {
    this.setState({ nameSearchValue: event.target.value })
  }

  storeSelectedVenue = event => {
    this.setState({ selectedVenueId: event.target.value })
  }

  onPreviousPageClick = () => {
    const { page } = this.state
    this.setState({ page: page - 1 }, () => {
      this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
    })
  }

  onNextPageClick = () => {
    const { page } = this.state
    this.setState({ page: page + 1 }, () => {
      this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
    })
  }

  render() {
    const {
      currentUser,
      handleOnDeactivateAllVenueOffersClick,
      handleOnActivateAllVenueOffersClick,
      offers,
      query,
    } = this.props

    const { isAdmin } = currentUser || {}
    const { venueId } = translateQueryParamsToApiParams(query.parse())
    const {
      nameSearchValue,
      offersCount,
      page,
      pageCount,
      isLoading,
      selectedVenueId,
      venueOptions,
    } = this.state

    const actionLink = !isAdmin ? (
      <Link
        className="cta button is-primary"
        to="/offres/creation"
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
        <form onSubmit={this.handleOnSubmit}>
          <TextInput
            label="Nom de l’offre"
            name="offre"
            onChange={this.storeNameSearchValue}
            placeholder="Rechercher par nom d’offre"
            value={nameSearchValue}
          />
          <Select
            defaultOption={ALL_VENUES_OPTION}
            handleSelection={this.storeSelectedVenue}
            label="Lieu"
            name="lieu"
            options={venueOptions}
            selectedValue={selectedVenueId}
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

        <div className="offers-count">
          {`${offersCount} ${offersCount <= 1 ? 'offre' : 'offres'}`}
        </div>

        <div className="section">
          {offers.length > 0 && venueId && (
            <div className="offers-list-actions">
              <button
                className="button deactivate is-tertiary is-small"
                onClick={handleOnDeactivateAllVenueOffersClick(venueId)}
                type="button"
              >
                {'Désactiver toutes les offres'}
              </button>

              <button
                className="button activate is-tertiary is-small"
                onClick={handleOnActivateAllVenueOffersClick(venueId)}
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
                      refreshOffers={this.getPaginatedOffersWithFilters}
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
  query: PropTypes.shape({
    change: PropTypes.func.isRequired,
    parse: PropTypes.func.isRequired,
  }).isRequired,
  saveSearchFilters: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }),
}

export default Offers
