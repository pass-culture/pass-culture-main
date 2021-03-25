import { endOfDay } from 'date-fns'
import { utcToZonedTime } from 'date-fns-tz'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Link } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import ActionsBarPortal from 'components/layout/ActionsBarPortal/ActionsBarPortal'
import Icon from 'components/layout/Icon'
import Select from 'components/layout/inputs/Select'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'
import { fetchAllVenuesByProUser, formatAndOrderVenues } from 'repository/venuesService'
import { formatBrowserTimezonedDateAsUTC, getToday } from 'utils/date'
import { mapApiToBrowser, mapBrowserToApi, translateQueryParamsToApiParams } from 'utils/translate'

import PeriodSelector from '../../../layout/inputs/PeriodSelector/PeriodSelector'

import {
  ADMINS_DISABLED_FILTERS_MESSAGE,
  ALL_TYPES_OPTION,
  ALL_VENUES_OPTION,
  CREATION_MODES_FILTERS,
  DEFAULT_CREATION_MODE,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
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
        status: searchFilters.status
          ? mapBrowserToApi[searchFilters.status]
          : DEFAULT_SEARCH_FILTERS.status,
        creationMode: searchFilters.creationMode
          ? mapBrowserToApi[searchFilters.creationMode]
          : DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate:
          searchFilters.periodBeginningDate || DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: searchFilters.periodEndingDate || DEFAULT_SEARCH_FILTERS.periodEndingDate,
      },
      offerer: null,
      venueOptions: [],
      isStatusFiltersVisible: false,
      areAllOffersSelected: false,
      typeOptions: [],
      selectedOfferIds: [],
    }
  }

  componentDidMount() {
    const { searchFilters } = this.state
    const { getOfferer } = this.props

    if (searchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId) {
      getOfferer(searchFilters.offererId).then(offerer => this.setState({ offerer }))
    }

    this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
    this.fetchAndFormatVenues(searchFilters.offererId)
    this.fetchTypeOptions()
  }

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (notification && notification.tag === 'offers-activation') {
      closeNotification()
    }
  }

  updateUrlMatchingState = () => {
    const { query } = this.props

    const { searchFilters, page } = this.state
    let queryParams = Object.keys(searchFilters).reduce((params, field) => {
      return {
        ...params,
        [mapApiToBrowser[field]]:
          searchFilters[field] === DEFAULT_SEARCH_FILTERS[field] ? null : searchFilters[field],
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
      page: parseInt(page),
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

  hasSearchFilters(searchFilters, filterNames = Object.keys(searchFilters)) {
    return filterNames
      .map(
        filterName =>
          searchFilters[filterName] !==
          { ...DEFAULT_SEARCH_FILTERS, page: DEFAULT_PAGE }[filterName]
      )
      .includes(true)
  }

  isAdminForbidden(searchFilters) {
    const { currentUser } = this.props
    return currentUser.isAdmin && !this.hasSearchFilters(searchFilters, ['venueId', 'offererId'])
  }

  handleOffererFilterRemoval = () => {
    const newSearchFilters = {
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
      status: this.getDefaultStatusIfNecessary(this.state.searchFilters.venueId),
    }
    this.setSearchFilters(newSearchFilters)
    this.setState({ offerer: null, page: DEFAULT_PAGE }, () => {
      this.getPaginatedOffersWithFilters({ shouldTriggerSpinner: true })
      this.fetchAndFormatVenues()
    })
  }

  getDefaultStatusIfNecessary(venueId, offererId = DEFAULT_SEARCH_FILTERS.offererId) {
    const isVenueFilterSelected = venueId !== DEFAULT_SEARCH_FILTERS.venueId
    const isOffererFilterApplied = offererId !== DEFAULT_SEARCH_FILTERS.offererId
    const isFilterByVenuOrOfferer = isVenueFilterSelected || isOffererFilterApplied

    return this.props.currentUser.isAdmin && !isFilterByVenuOrOfferer
      ? DEFAULT_SEARCH_FILTERS.status
      : this.state.searchFilters.status
  }

  setSearchFilters(newSearchFilters) {
    const { searchFilters } = this.state
    const updatedSearchFilters = {
      ...searchFilters,
      ...newSearchFilters,
    }
    this.setState({ searchFilters: updatedSearchFilters })
  }

  storeNameSearchValue = event => {
    this.setSearchFilters({ name: event.target.value })
  }

  storeSelectedVenue = event => {
    const selectedVenueId = event.target.value
    const newSearchFilters = {
      venueId: selectedVenueId,
      status: this.getDefaultStatusIfNecessary(selectedVenueId, this.state.searchFilters.offererId),
    }
    this.setSearchFilters(newSearchFilters)
  }

  storeSelectedType = event => {
    this.setSearchFilters({ typeId: event.target.value })
  }

  updateStatusFilter = selectedStatus => {
    this.setSearchFilters({ status: selectedStatus })
  }

  storeCreationMode = event => {
    this.setSearchFilters({ creationMode: event.target.value })
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
    const { selectedOfferIds } = this.state
    let newSelectedOfferIds = [...selectedOfferIds]
    if (selected) {
      newSelectedOfferIds.push(offerId)
    } else {
      const offerIdIndex = newSelectedOfferIds.indexOf(offerId)
      newSelectedOfferIds.splice(offerIdIndex, 1)
    }

    this.setState({ selectedOfferIds: newSelectedOfferIds })
  }

  selectAllOffers = () => {
    const { offers } = this.props
    const { areAllOffersSelected } = this.state

    const selectedOfferIds = areAllOffersSelected ? [] : offers.map(offer => offer.id)
    this.setState({ selectedOfferIds: selectedOfferIds })

    this.toggleSelectAllCheckboxes()
  }

  toggleSelectAllCheckboxes = () => {
    const { areAllOffersSelected } = this.state
    this.setState({ areAllOffersSelected: !areAllOffersSelected })
  }

  setIsStatusFiltersVisible = isStatusFiltersVisible => {
    this.setState({ isStatusFiltersVisible })
  }

  changePeriodBeginningDateValue = periodBeginningDate => {
    const dateToFilter = periodBeginningDate
      ? formatBrowserTimezonedDateAsUTC(periodBeginningDate)
      : DEFAULT_SEARCH_FILTERS.periodBeginningDate
    this.setSearchFilters({ periodBeginningDate: dateToFilter })
  }

  changePeriodEndingDateValue = periodEndingDate => {
    const dateToFilter = periodEndingDate
      ? formatBrowserTimezonedDateAsUTC(endOfDay(periodEndingDate))
      : DEFAULT_SEARCH_FILTERS.periodEndingDate
    this.setSearchFilters({ periodEndingDate: dateToFilter })
  }

  clearSelectedOfferIds = () => {
    this.setState({ selectedOfferIds: [] })
  }

  renderSearchFilters = () => {
    const { searchFilters, typeOptions, venueOptions, offerer } = this.state

    return (
      <Fragment>
        {offerer && (
          <span className="offerer-filter">
            {offerer.name}
            <button
              onClick={this.handleOffererFilterRemoval}
              type="button"
            >
              <Icon
                alt="Supprimer le filtre par structure"
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
            <PeriodSelector
              changePeriodBeginningDateValue={this.changePeriodBeginningDateValue}
              changePeriodEndingDateValue={this.changePeriodEndingDateValue}
              isDisabled={false}
              label="Période de l’évènement"
              maxDateBeginning={
                searchFilters.periodEndingDate
                  ? utcToZonedTime(searchFilters.periodEndingDate, 'UTC')
                  : undefined
              }
              minDateEnding={
                searchFilters.periodBeginningDate
                  ? utcToZonedTime(searchFilters.periodBeginningDate, 'UTC')
                  : undefined
              }
              periodBeginningDate={
                searchFilters.periodBeginningDate
                  ? utcToZonedTime(searchFilters.periodBeginningDate, 'UTC')
                  : undefined
              }
              periodEndingDate={
                searchFilters.periodEndingDate
                  ? utcToZonedTime(searchFilters.periodEndingDate, 'UTC')
                  : undefined
              }
              todayDate={getToday()}
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
      </Fragment>
    )
  }

  renderNoOffers = () => {
    return (
      <div className="no-search-results">
        <Icon
          className="image"
          svg="ico-ticket-gray"
        />

        <p className="highlight">
          {'Aucune offre'}
        </p>
        <p>
          {"Vous n'avez pas encore créé d'offre."}
        </p>

        <Link
          className="primary-button with-icon"
          to="/offres/creation"
        >
          <AddOfferSvg />
          {'Créer ma première offre'}
        </Link>
      </div>
    )
  }

  renderTableHead = () => {
    const { offers, savedSearchFilters } = this.props
    const { areAllOffersSelected, isStatusFiltersVisible, searchFilters } = this.state

    return (
      <thead>
        <tr>
          <th className="th-checkbox">
            <input
              checked={areAllOffersSelected}
              className="select-offer-checkbox"
              disabled={this.isAdminForbidden(savedSearchFilters) || !offers.length}
              id="select-offer-checkbox"
              onChange={this.selectAllOffers}
              type="checkbox"
            />
          </th>
          <th
            className={`th-checkbox-label ${
              this.isAdminForbidden(savedSearchFilters) || !offers.length ? 'label-disabled' : ''
            }`}
          >
            <label
              htmlFor="select-offer-checkbox"
              title={
                this.isAdminForbidden(savedSearchFilters)
                  ? ADMINS_DISABLED_FILTERS_MESSAGE
                  : undefined
              }
            >
              {areAllOffersSelected ? 'Tout désélectionner' : 'Tout sélectionner'}
            </label>
          </th>
          <th />
          <th>
            {'Lieu'}
          </th>
          <th>
            {'Stock'}
          </th>
          <th className="th-with-filter">
            <StatusFiltersButton
              disabled={this.isAdminForbidden(searchFilters)}
              isStatusFiltersVisible={isStatusFiltersVisible}
              refreshOffers={this.handleOnSubmit}
              setIsStatusFiltersVisible={this.setIsStatusFiltersVisible}
              status={searchFilters.status}
              updateStatusFilter={this.updateStatusFilter}
            />
          </th>
          <th />
          <th />
        </tr>
      </thead>
    )
  }

  renderTable = () => {
    const { offers } = this.props
    const { areAllOffersSelected, offersCount, page, pageCount, selectedOfferIds } = this.state

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
    const { searchFilters } = this.state
    const hadOffererFilter = this.hasSearchFilters(searchFilters)

    this.setState({ offerer: null })
    this.setState({ searchFilters: { ...DEFAULT_SEARCH_FILTERS } }, () => {
      if (hadOffererFilter) {
        this.fetchAndFormatVenues()
      }
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
            className="reset-filters-link"
            onClick={this.resetFilters}
            to="/offres"
          >
            {'afficher toutes les offres'}
          </Link>
        </p>
      </div>
    </div>
  )

  renderSearchResults = () => {
    const { offers, savedSearchFilters } = this.props
    const { isLoading } = this.state

    if (isLoading) {
      return <Spinner />
    }

    if (offers.length) {
      return this.renderTable()
    }

    if (this.hasSearchFilters(savedSearchFilters)) {
      return this.renderNoResultsForFilters()
    }

    return null
  }

  render() {
    const { currentUser, offers, savedSearchFilters } = this.props
    const { areAllOffersSelected, isLoading, offersCount, selectedOfferIds } = this.state
    const { isAdmin } = currentUser || {}

    const hasOffers = !!offers.length || this.hasSearchFilters(savedSearchFilters)
    const displayOffers = isLoading || hasOffers

    const actionLink =
      !displayOffers || isAdmin ? null : (
        <Link
          className="primary-button with-icon"
          to="/offres/creation"
        >
          <AddOfferSvg />
          {'Créer une offre'}
        </Link>
      )

    const nbSelectedOffers = areAllOffersSelected ? offersCount : selectedOfferIds.length

    return (
      <AppLayout
        layoutConfig={{
          pageName: 'offers',
        }}
      >
        <PageTitle title="Vos offres" />
        <Titles
          action={actionLink}
          title="Offres"
        />
        <ActionsBarPortal isVisible={nbSelectedOffers > 0}>
          <ActionsBarContainer
            areAllOffersSelected={areAllOffersSelected}
            clearSelectedOfferIds={this.clearSelectedOfferIds}
            nbSelectedOffers={areAllOffersSelected ? offersCount : selectedOfferIds.length}
            refreshOffers={this.getPaginatedOffersWithFilters}
            selectedOfferIds={selectedOfferIds}
            toggleSelectAllCheckboxes={this.toggleSelectAllCheckboxes}
          />
        </ActionsBarPortal>
        {displayOffers ? (
          <Fragment>
            <h3 className="op-title">
              {'Rechercher une offre'}
            </h3>
            {this.hasSearchFilters(savedSearchFilters) ? (
              <Link
                className="reset-filters-link"
                onClick={this.resetFilters}
                to="/offres"
              >
                {'Réinitialiser les filtres'}
              </Link>
            ) : (
              <span className="reset-filters-link disabled">
                {'Réinitialiser les filtres'}
              </span>
            )}

            {this.renderSearchFilters()}

            <div className="section">
              {this.renderSearchResults()}
            </div>
          </Fragment>
        ) : (
          this.renderNoOffers()
        )}
      </AppLayout>
    )
  }
}

Offers.defaultProps = {
  venue: undefined,
}

Offers.propTypes = {
  closeNotification: PropTypes.func.isRequired,
  currentUser: PropTypes.shape().isRequired,
  getOfferer: PropTypes.func.isRequired,
  loadOffers: PropTypes.func.isRequired,
  notification: PropTypes.shape().isRequired,
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
  venue: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }),
}

export default Offers
