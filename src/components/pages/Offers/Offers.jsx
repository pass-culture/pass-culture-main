import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import Select from 'components/layout/inputs/Select'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import Main from 'components/layout/Main'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'
import { fetchAllVenuesByProUser, formatAndOrderVenues } from 'repository/venuesService'
import { mapApiToBrowser, mapBrowserToApi, translateQueryParamsToApiParams } from 'utils/translate'

import {
  DEFAULT_SEARCH_FILTERS,
  ALL_OFFERERS,
  ALL_VENUES_OPTION,
  ALL_TYPES_OPTION,
  CREATION_MODES_FILTERS,
  DEFAULT_CREATION_MODE,
  DEFAULT_PAGE,
} from './_constants'
import ActionsBarContainer from './ActionsBar/ActionsBarContainer'
import OfferItemContainer from './OfferItem/OfferItemContainer'
import StatusFiltersButton from './StatusFiltersButton'

class Offers extends PureComponent {
  constructor(props) {
    super(props)

    const { page, ...searchFilters } = translateQueryParamsToApiParams(props.query.parse())

    this.state = {
      isLoading: false,
      offersCount: 0,
      page: page || DEFAULT_PAGE,
      pageCount: null,
      searchFilters: {
        name: searchFilters.name || DEFAULT_SEARCH_FILTERS.name,
        offererId: searchFilters.offererId || DEFAULT_SEARCH_FILTERS.offererId,
        venueId: searchFilters.venueId || DEFAULT_SEARCH_FILTERS.venueId,
        typeId: searchFilters.typeId || DEFAULT_SEARCH_FILTERS.typeId,
        status: searchFilters.status || DEFAULT_SEARCH_FILTERS.status,
        creationMode: searchFilters.creationMode
          ? mapBrowserToApi[searchFilters.creationMode]
          : DEFAULT_SEARCH_FILTERS.creationMode,
      },
      offerer: null,
      venueOptions: [],
      isStatusFiltersVisible: false,
      areAllOffersSelected: false,
      typeOptions: [],
    }
  }

  componentDidMount() {
    const { searchFilters } = this.state
    const { getOfferer } = this.props

    if (searchFilters.offererId !== ALL_OFFERERS) {
      getOfferer(searchFilters.offererId).then(offerer => this.setState({ offerer }))
    }

    this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
    this.fetchAndFormatVenues(searchFilters.offererId)
    this.fetchTypeOptions()
  }

  componentWillUnmount() {
    const { closeNotification, notification, setSelectedOfferIds, hideActionsBar } = this.props
    if (notification && notification.tag === 'offers-activation') {
      closeNotification()
    }

    setSelectedOfferIds([])
    hideActionsBar()
  }

  updateUrlMatchingState = () => {
    const { query } = this.props

    const { searchFilters, page } = this.state
    let queryParams = Object.keys(searchFilters).reduce((params, field) => {
      if (searchFilters[field] === DEFAULT_SEARCH_FILTERS[field]) {
        return params
      }
      return {
        ...params,
        [mapApiToBrowser[field]]: searchFilters[field],
      }
    }, {})

    const fieldsWithTranslatedValues = ['statut', 'creation']
    fieldsWithTranslatedValues.forEach(field => {
      if (queryParams[field]) {
        queryParams[field] = mapApiToBrowser[queryParams[field]]
      }
    })

    if (page !== DEFAULT_PAGE) {
      queryParams.page = page
    }

    query.change(queryParams)
  }

  fetchTypeOptions = () => {
    pcapi.loadTypes().then(types => {
      let typeOptions = types.map(type => ({
        id: type.value,
        displayName: type.proLabel,
      }))
      this.setState({
        typeOptions: typeOptions.sort((a, b) => a.displayName.localeCompare(b.displayName)),
      })
    })
  }

  loadAndUpdateOffers() {
    const { loadOffers } = this.props
    const { searchFilters, page } = this.state

    loadOffers({ ...searchFilters, page })
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
    const { saveSearchFilters } = this.props
    const { searchFilters, page } = this.state
    saveSearchFilters({
      ...searchFilters,
      page,
    })
    shouldTriggerSpinner && this.setState({ isLoading: true })
    this.loadAndUpdateOffers()
  }

  fetchAndFormatVenues = offererId => {
    fetchAllVenuesByProUser(offererId).then(venues =>
      this.setState({ venueOptions: formatAndOrderVenues(venues) })
    )
  }

  handleOnSubmit = event => {
    event.preventDefault()

    this.setState(
      {
        page: DEFAULT_PAGE,
      },
      () => {
        this.setIsStatusFiltersVisible(false)
        this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
      }
    )
  }

  handleOffererFilterRemoval = () => {
    this.setSearchFilters('offererId', ALL_OFFERERS)
    this.setState({ offerer: null, page: DEFAULT_PAGE }, () => {
      this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
      this.fetchAndFormatVenues()
    })
  }

  setSearchFilters(field, value) {
    const { searchFilters } = this.state
    const updatedSearchFilters = {
      ...searchFilters,
      [field]: value,
    }
    this.setState({ searchFilters: updatedSearchFilters })
  }

  storeNameSearchValue = event => {
    this.setSearchFilters('name', event.target.value)
  }

  storeSelectedVenue = event => {
    this.setSearchFilters('venueId', event.target.value)
  }

  storeSelectedType = event => {
    this.setSearchFilters('typeId', event.target.value)
  }

  updateStatusFilter = selectedStatus => {
    this.setSearchFilters('status', selectedStatus)
  }

  storeCreationMode = event => {
    this.setSearchFilters('creationMode', event.target.value)
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

  selectOffer = (offerId, selected) => {
    const { hideActionsBar, setSelectedOfferIds, selectedOfferIds, showActionsBar } = this.props

    let newSelectedOfferIds = [...selectedOfferIds]
    if (selected) {
      newSelectedOfferIds.push(offerId)
    } else {
      const offerIdIndex = newSelectedOfferIds.indexOf(offerId)
      newSelectedOfferIds.splice(offerIdIndex, 1)
    }
    setSelectedOfferIds(newSelectedOfferIds)
    newSelectedOfferIds.length ? showActionsBar() : hideActionsBar()
  }

  selectAllOffers = () => {
    const { offers, showActionsBar, setSelectedOfferIds, hideActionsBar } = this.props
    const { areAllOffersSelected } = this.state

    const selectedOfferIds = areAllOffersSelected ? [] : offers.map(offer => offer.id)
    selectedOfferIds.length ? showActionsBar() : hideActionsBar()
    setSelectedOfferIds(selectedOfferIds)

    this.toggleSelectAllCheckboxes()
  }

  toggleSelectAllCheckboxes = () => {
    const { areAllOffersSelected } = this.state
    this.setState({ areAllOffersSelected: !areAllOffersSelected })
  }

  getOffersActionsBar = () => {
    const { selectedOfferIds } = this.props
    const { areAllOffersSelected, offersCount } = this.state

    return (
      <ActionsBarContainer
        areAllOffersSelected={areAllOffersSelected}
        nbSelectedOffers={areAllOffersSelected ? offersCount : selectedOfferIds.length}
        refreshOffers={this.getPaginatedOffersWithFilters}
        toggleSelectAllCheckboxes={this.toggleSelectAllCheckboxes}
      />
    )
  }

  setIsStatusFiltersVisible = isStatusFiltersVisible => {
    this.setState({ isStatusFiltersVisible })
  }

  renderTableHead = () => {
    const { currentUser, offers } = this.props
    const { areAllOffersSelected, isStatusFiltersVisible, searchFilters } = this.state
    return (
      <thead>
        <tr>
          {currentUser.isAdmin ? (
            <Fragment>
              <th />
              <th />
            </Fragment>
          ) : (
            <Fragment>
              <th className="th-checkbox">
                {offers.length ? (
                  <input
                    checked={areAllOffersSelected}
                    className="select-offer-checkbox"
                    id="select-offer-checkbox"
                    onChange={this.selectAllOffers}
                    type="checkbox"
                  />
                ) : null}
              </th>
              <th className="th-checkbox-label">
                <label htmlFor="select-offer-checkbox">
                  {areAllOffersSelected ? 'Tout désélectionner' : 'Tout sélectionner'}
                </label>
              </th>
            </Fragment>
          )}
          <th />
          <th>
            {'Lieu'}
          </th>
          <th>
            {'Stock'}
          </th>
          {currentUser.isAdmin ? (
            <th>
              {'Statut'}
            </th>
          ) : (
            <th className="th-with-filter">
              <StatusFiltersButton
                isStatusFiltersVisible={isStatusFiltersVisible}
                refreshOffers={this.handleOnSubmit}
                setIsStatusFiltersVisible={this.setIsStatusFiltersVisible}
                status={searchFilters.status}
                updateStatusFilter={this.updateStatusFilter}
              />
            </th>
          )}
          <th />
          <th />
        </tr>
      </thead>
    )
  }

  renderTable = () => {
    const { offers, selectedOfferIds } = this.props
    const { areAllOffersSelected, offersCount, page, pageCount } = this.state

    return (
      <Fragment>
        <div className="offers-count">
          {`${offersCount} ${offersCount <= 1 ? 'offre' : 'offres'}`}
        </div>
        <table>
          {this.renderTableHead()}
          <tbody className="offers-list">
            {offers.map(offer => (
              <OfferItemContainer
                disabled={areAllOffersSelected}
                isSelected={areAllOffersSelected || selectedOfferIds.includes(offer.id)}
                key={offer.id}
                offer={offer}
                selectOffer={this.selectOffer}
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
    )
  }

  resetFilters = () => {
    this.setState({ offerer: null })
    this.setState({ searchFilters: { ...DEFAULT_SEARCH_FILTERS } }, () => {
      this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
    })
  }

  renderNoResultsForFilters = () => (
    <div>
      <table>
        {this.renderTableHead()}
      </table>

      <div className="search-no-results">
        <Icon
          alt="Illustration de recherche"
          svg="ico-search-gray"
        />
        <p>
          {'Aucune offre trouvée pour votre recherche'}
        </p>
        <p>
          {'Vous pouvez modifer votre recherche ou'}
          <br />
          <Link
            className="tertiary-link primary-color"
            onClick={this.resetFilters}
            to="/offres"
          >
            {'afficher toutes les offres'}
          </Link>
        </p>
      </div>
    </div>
  )

  hasSearchFilters = () => {
    // We dont want "no results for filters" to disappear on filters change
    // so we need to use saved search filters and not local state ones.
    const { savedSearchFilters } = this.props
    return Object.keys(savedSearchFilters)
      .map(
        field =>
          savedSearchFilters[field] !== { ...DEFAULT_SEARCH_FILTERS, page: DEFAULT_PAGE }[field]
      )
      .includes(true)
  }

  renderSearchResults = () => {
    const { offers } = this.props
    const { isLoading } = this.state

    if (isLoading) {
      return <Spinner />
    }

    if (offers.length) {
      return this.renderTable()
    }

    if (this.hasSearchFilters()) {
      return this.renderNoResultsForFilters()
    }

    return null
  }

  render() {
    const { currentUser } = this.props
    const { isAdmin } = currentUser || {}
    const { searchFilters, offerer, typeOptions, venueOptions } = this.state

    const actionLink = isAdmin ? null : (
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
    )

    return (
      <Main
        PageActionsBar={this.getOffersActionsBar}
        id="offers"
        name="offers"
      >
        <PageTitle title="Vos offres" />
        <Titles
          action={actionLink}
          title="Offres"
        />
        <span className="subtitle-container">
          <h3 className="subtitle">
            {'Rechercher une offre'}
          </h3>
          <Link
            className={`tertiary-link ${this.hasSearchFilters() ? 'primary-color' : ''}`}
            onClick={this.resetFilters}
            to="/offres"
          >
            {'Réinitialiser les filtres'}
            {this.hasSearchFilters()}
          </Link>
        </span>
        {offerer && (
          <span className="offerer-filter">
            {offerer.name}
            <button
              onClick={this.handleOffererFilterRemoval}
              type="button"
            >
              <Icon
                alt="Supprimer le filtre"
                svg="ico-close-b"
              />
            </button>
          </span>
        )}
        <form onSubmit={this.handleOnSubmit}>
          <TextInput
            label="Nom de l’offre"
            name="offre"
            onChange={this.storeNameSearchValue}
            placeholder="Rechercher par nom d’offre"
            value={searchFilters.name}
          />
          <div className="form-row">
            <Select
              defaultOption={ALL_VENUES_OPTION}
              handleSelection={this.storeSelectedVenue}
              label="Lieu"
              name="lieu"
              options={venueOptions}
              selectedValue={searchFilters.venueId}
            />
            <Select
              defaultOption={ALL_TYPES_OPTION}
              handleSelection={this.storeSelectedType}
              label="Catégories"
              name="type"
              options={typeOptions}
              selectedValue={searchFilters.typeId}
            />
            <Select
              defaultOption={DEFAULT_CREATION_MODE}
              handleSelection={this.storeCreationMode}
              label="Mode de création"
              name="creationMode"
              options={CREATION_MODES_FILTERS}
              selectedValue={searchFilters.creationMode}
            />
          </div>
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

        <div className="section">
          {this.renderSearchResults()}
        </div>
      </Main>
    )
  }
}

Offers.defaultProps = {
  selectedOfferIds: [],
  venue: undefined,
}

Offers.propTypes = {
  closeNotification: PropTypes.func.isRequired,
  currentUser: PropTypes.shape().isRequired,
  hideActionsBar: PropTypes.func.isRequired,
  loadOffers: PropTypes.func.isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  query: PropTypes.shape({
    change: PropTypes.func.isRequired,
    parse: PropTypes.func.isRequired,
  }).isRequired,
  saveSearchFilters: PropTypes.func.isRequired,
  savedSearchFilters: PropTypes.shape({
    name: PropTypes.string,
    offererId: PropTypes.string,
    venueId: PropTypes.string,
    typeId: PropTypes.string,
    status: PropTypes.string,
    creationMode: PropTypes.string,
  }).isRequired,
  selectedOfferIds: PropTypes.arrayOf(PropTypes.string),
  setSelectedOfferIds: PropTypes.func.isRequired,
  showActionsBar: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }),
}

export default Offers
