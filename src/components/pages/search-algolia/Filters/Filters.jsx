import PropTypes from 'prop-types'
import Slider, { Range } from 'rc-slider'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import Icon from '../../../layout/Icon/Icon'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from '../Criteria/criteriaEnums'
import CriteriaLocation from '../CriteriaLocation/CriteriaLocation'
import { checkIfAroundMe } from '../utils/checkIfAroundMe'
import FilterCheckbox from './FilterCheckbox/FilterCheckbox'
import { DATE_FILTER, PRICE_FILTER } from './filtersEnums'
import FilterToggle from './FilterToggle/FilterToggle'
import { DEFAULT_RADIUS_IN_KILOMETERS } from '../../../../vendor/algolia/filters'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../layout/Header/HeaderContainer'

export class Filters extends PureComponent {
  constructor(props) {
    super(props)

    const {
      aroundRadius,
      date,
      isOfferFilteredByDate,
      isSearchAroundMe,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      sortBy,
    } = props.initialFilters
    const offerCategories = this.buildCategoriesStateFromProps()
    this.state = {
      areCategoriesVisible: true,
      filters: {
        aroundRadius,
        date,
        isOfferFilteredByDate,
        isSearchAroundMe,
        offerCategories,
        offerIsFree,
        offerIsDuo,
        offerTypes,
        priceRange,
        sortBy,
      },
      offers: props.offers,
    }
  }

  buildCategoriesStateFromProps = () => {
    const { initialFilters } = this.props

    return initialFilters.offerCategories.reduce((object, arrayValue) => {
      object[arrayValue] = true
      return object
    }, {})
  }

  fetchOffers = ({
    aroundRadius,
    date,
    geolocation,
    isSearchAroundMe,
    keywords,
    offerCategories,
    offerIsDuo,
    offerIsFree,
    offerTypes,
    priceRange,
    sortBy,
  }) => {
    const { showFailModal } = this.props
    fetchAlgolia({
      aroundRadius,
      date,
      geolocation,
      isSearchAroundMe,
      keywords,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      sortBy,
    })
      .then(offers => {
        this.setState({
          offers: offers,
        })
      })
      .catch(() => {
        showFailModal()
      })
  }

  handleOffersFetchAndUrlUpdate = () => {
    const { history, geolocation, query } = this.props
    const { filters } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    const {
      aroundRadius,
      date,
      isSearchAroundMe,
      isOfferFilteredByDate,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      sortBy,
    } = filters
    const offerCategories = this.getSelectedCategories()
    const dateFilter = isOfferFilteredByDate ? date : null

    this.fetchOffers({
      aroundRadius,
      date: dateFilter,
      geolocation,
      isSearchAroundMe,
      keywords,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      sortBy,
    })

    const search = this.buildSearchParameter()
    history.replace({ search })
  }

  buildSearchParameter = () => {
    const { filters } = this.state
    const { query } = this.props
    const { isSearchAroundMe, sortBy } = filters
    const offerCategories = this.getSelectedCategories()
    const autourDeMoi = checkIfAroundMe(isSearchAroundMe)
    const categories = offerCategories.join(';') || ''
    const tri = sortBy
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''
    return `?mots-cles=${keywords}&autour-de-moi=${autourDeMoi}&tri=${tri}&categories=${categories}`
  }

  resetFilters = () => {
    const { initialFilters } = this.props

    this.setState(
      {
        filters: {
          ...initialFilters,
          aroundRadius: DEFAULT_RADIUS_IN_KILOMETERS,
          date: {
            option: DATE_FILTER.TODAY.value,
            selectedDate: null,
          },
          isSearchAroundMe: false,
          isOfferFilteredByDate: false,
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  getSelectedCategories = () => {
    const { filters } = this.state
    const { offerCategories } = filters

    return Object.keys(offerCategories).filter(categoryKey => offerCategories[categoryKey])
  }

  buildNumberOfResults = () => {
    const {
      offers: { nbHits },
    } = this.state

    if (nbHits === 0) {
      return 'Aucun résultat'
    }

    const results = nbHits < 1000 ? `${nbHits}` : `999+`
    return `Afficher les ${results} résultats`
  }

  buildGeolocationFilter = () => {
    const { filters } = this.state
    return filters.isSearchAroundMe ? 'Autour de moi' : 'Partout'
  }

  getActiveCriterionLabel = () => {
    const { filters } = this.state
    return filters.isSearchAroundMe
      ? GEOLOCATION_CRITERIA.AROUND_ME.label
      : GEOLOCATION_CRITERIA.EVERYWHERE.label
  }

  getNumberOfSelectedFilters = filter => {
    let counter = 0

    Object.keys(filter).forEach(key => {
      if (filter[key] === true) {
        counter++
      }
    })
    return counter
  }

  getPriceRangeCounter(priceRange) {
    const [lowestPrice, highestPrice] = priceRange
    const [defaultLowestPrice, defaultHighestPrice] = PRICE_FILTER.DEFAULT_RANGE
    return lowestPrice !== defaultLowestPrice || highestPrice !== defaultHighestPrice ? 1 : 0
  }

  getNumberFromBoolean = boolean => (boolean === true ? 1 : 0)

  handleGeolocationCriterionSelection = criterionKey => {
    const { filters } = this.state
    const { history } = this.props

    this.setState(
      {
        filters: {
          ...filters,
          isSearchAroundMe:
            GEOLOCATION_CRITERIA[criterionKey].label === GEOLOCATION_CRITERIA.AROUND_ME.label,
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
        const search = this.buildSearchParameter()
        history.push(`/recherche/resultats/filtres${search}`)
      }
    )
  }

  handleGoToGeolocationFilter = () => {
    const { history } = this.props
    const {
      location: { search = '' },
    } = history
    history.push(`/recherche/resultats/filtres/localisation${search}`)
  }

  handleFilterOffers = () => {
    const { history, updateFilteredOffers, updateFilters, updateNumberOfActiveFilters } = this.props
    const {
      location: { search = '' },
    } = history
    const { filters, offers } = this.state
    const {
      isOfferFilteredByDate,
      isSearchAroundMe,
      offerCategories,
      offerTypes,
      offerIsDuo,
      offerIsFree,
      priceRange,
    } = filters
    const updatedFilters = { ...filters }
    updatedFilters.offerCategories = this.getSelectedCategories()
    const geolocationFilterCounter = this.getNumberFromBoolean(isSearchAroundMe)
    const offerTypesFilterCounter = this.getNumberOfSelectedFilters(offerTypes)
    const offerCategoriesFilterCounter = this.getNumberOfSelectedFilters(offerCategories)
    const offerIsDuoFilterCounter = this.getNumberFromBoolean(offerIsDuo)
    const offerIsFreeFilterCounter = this.getNumberFromBoolean(offerIsFree)
    const priceRangeFilterCounter = this.getPriceRangeCounter(priceRange)
    const dateFilterCounter = this.getNumberFromBoolean(isOfferFilteredByDate)
    const numberOfActiveFilters =
      offerTypesFilterCounter +
      offerCategoriesFilterCounter +
      geolocationFilterCounter +
      offerIsDuoFilterCounter +
      offerIsFreeFilterCounter +
      priceRangeFilterCounter +
      dateFilterCounter

    updateFilters(updatedFilters)
    updateFilteredOffers(offers)
    updateNumberOfActiveFilters(numberOfActiveFilters)
    history.push(`/recherche/resultats${search}`)
  }

  handleOnTypeChange = event => {
    const { name, checked } = event.target
    const { filters } = this.state
    const { offerTypes } = filters

    this.setState(
      {
        filters: {
          ...filters,
          offerTypes: {
            ...offerTypes,
            [name]: checked,
          },
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  handleOnCategoryChange = event => {
    const { name, checked } = event.target
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          offerCategories: {
            ...filters.offerCategories,
            [name]: checked,
          },
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  handleToggleCategories = () => () => {
    this.setState(prevState => ({ areCategoriesVisible: !prevState.areCategoriesVisible }))
  }

  handleOnToggle = event => {
    const { name, checked } = event.target
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          [name]: checked,
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  handleDateToggle = event => {
    const { checked } = event.target
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          isOfferFilteredByDate: checked,
          date: {
            ...filters.date,
            selectedDate: new Date(),
          },
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  handleRadiusSlide = value => {
    const { filters } = this.state

    this.setState({
      filters: {
        ...filters,
        aroundRadius: value,
      },
    })
  }

  handleRadiusAfterSlide = () => {
    this.handleOffersFetchAndUrlUpdate()
  }

  handlePriceSlide = priceRange => {
    const { filters } = this.state

    this.setState({
      filters: {
        ...filters,
        priceRange,
      },
    })
  }

  handleDateSelection = event => {
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          date: {
            selectedDate: new Date(),
            option: event.target.value,
          },
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  handlePickedDate = momentDate => {
    const { filters } = this.state
    const selectedDate = momentDate.toDate()

    this.setState(
      {
        filters: {
          ...filters,
          date: {
            selectedDate,
            option: DATE_FILTER.USER_PICK.value,
          },
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
      }
    )
  }

  render() {
    const { areCategoriesVisible, filters, offers } = this.state
    const { nbHits } = offers
    const {
      aroundRadius,
      date,
      isOfferFilteredByDate,
      isSearchAroundMe,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
    } = filters
    const { history, match, geolocation } = this.props
    const { location } = history
    const { search = '' } = location
    const numberOfOfferTypesSelected = this.getNumberOfSelectedFilters(offerTypes)
    const numberOfOfferCategoriesSelected = this.getNumberOfSelectedFilters(offerCategories)
    const geolocationFilterCounter = this.getNumberFromBoolean(isSearchAroundMe)
    const offerIsDuoCounter = this.getNumberFromBoolean(offerIsDuo)
    const offerIsFreeCounter = this.getNumberFromBoolean(offerIsFree)
    const priceRangeCounter = this.getPriceRangeCounter(priceRange)
    const dateFilterCounter = this.getNumberFromBoolean(isOfferFilteredByDate)

    return (
      <main className="search-filters-page">
        <Switch>
          <Route path="/recherche/resultats/filtres/localisation">
            <CriteriaLocation
              activeCriterionLabel={this.getActiveCriterionLabel()}
              backTo={`/recherche/resultats/filtres${search}`}
              criteria={GEOLOCATION_CRITERIA}
              geolocation={geolocation}
              history={history}
              match={match}
              onCriterionSelection={this.handleGeolocationCriterionSelection}
              title="Localisation"
            />
          </Route>
          <Route path="/recherche/resultats/filtres">
            <div className="sf-header-wrapper">
              <HeaderContainer
                backTo={`/recherche/resultats${search}`}
                closeTo={null}
                reset={this.resetFilters}
                title="Filtrer"
              />
            </div>
            <ul className="sf-content-wrapper">
              <li>
                <h4 className="sf-title">
                  {'Localisation'}
                </h4>
                {geolocationFilterCounter > 0 && (
                  <span className="sf-selected-filter-counter">
                    {`(${geolocationFilterCounter})`}
                  </span>
                )}
                <button
                  className="sf-geolocation-button"
                  onClick={this.handleGoToGeolocationFilter}
                  type="button"
                >
                  {this.buildGeolocationFilter()}
                </button>
                {isSearchAroundMe && (
                  <span className="sf-warning-message">
                    {'Seules les offres Sorties et Physiques seront affichées'}
                  </span>
                )}
                <span className="sf-filter-separator" />
              </li>
              {isSearchAroundMe && (
                <li>
                  <h4 className="sf-title">
                    {'Rayon'}
                  </h4>
                  <h4 className="sf-slider-indicator">
                    {`${aroundRadius} km`}
                  </h4>
                  <div className="sf-slider-wrapper">
                    <Slider
                      max={100}
                      min={0}
                      onAfterChange={this.handleRadiusAfterSlide}
                      onChange={this.handleRadiusSlide}
                      value={aroundRadius}
                    />
                  </div>
                  <span className="sf-filter-separator" />
                </li>
              )}
              <li>
                <button
                  aria-label="Afficher les catégories"
                  aria-pressed={areCategoriesVisible}
                  className={`sf-category-title-wrapper ${
                    areCategoriesVisible ? 'sf-title-drop-down' : 'sf-title-drop-down-flipped'
                  }`}
                  onClick={this.handleToggleCategories()}
                  type="button"
                >
                  <h4>
                    {'Catégories'}
                  </h4>
                  {numberOfOfferCategoriesSelected > 0 && (
                    <span className="sf-selected-filter-counter">
                      {`(${numberOfOfferCategoriesSelected})`}
                    </span>
                  )}
                </button>
                {areCategoriesVisible && (
                  <ul
                    className="sf-filter-wrapper"
                    data-test="sf-categories-filter-wrapper"
                  >
                    {Object.values(CATEGORY_CRITERIA).map(categoryCriterion => {
                      if (categoryCriterion.label !== CATEGORY_CRITERIA.ALL.label) {
                        return (
                          <li key={categoryCriterion.facetFilter}>
                            <FilterCheckbox
                              checked={
                                offerCategories[categoryCriterion.facetFilter] ? true : false
                              }
                              className={`${
                                offerCategories[categoryCriterion.facetFilter]
                                  ? 'fc-label-checked'
                                  : 'fc-label'
                              }`}
                              id={categoryCriterion.facetFilter}
                              label={categoryCriterion.label}
                              name={categoryCriterion.facetFilter}
                              onChange={this.handleOnCategoryChange}
                            />
                          </li>
                        )
                      }
                    })}
                  </ul>
                )}
                <span className="sf-filter-separator" />
              </li>
              <li>
                <div className="sf-title-wrapper">
                  <h4 className="sf-title">
                    {"Type d'offres"}
                  </h4>
                  {numberOfOfferTypesSelected > 0 && (
                    <span className="sf-selected-filter-counter">
                      {`(${numberOfOfferTypesSelected})`}
                    </span>
                  )}
                </div>
                <ul
                  className="sf-filter-wrapper"
                  data-test="sf-offer-types-filter-wrapper"
                >
                  <li>
                    <FilterCheckbox
                      checked={offerTypes.isDigital}
                      className={`${offerTypes.isDigital ? 'fc-label-checked' : 'fc-label'}`}
                      id="isDigital"
                      label="Offres numériques"
                      name="isDigital"
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                  <li>
                    <FilterCheckbox
                      checked={offerTypes.isThing}
                      className={`${offerTypes.isThing ? 'fc-label-checked' : 'fc-label'}`}
                      id="isThing"
                      label="Offres physiques"
                      name="isThing"
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                  <li>
                    <FilterCheckbox
                      checked={offerTypes.isEvent}
                      className={`${offerTypes.isEvent ? 'fc-label-checked' : 'fc-label'}`}
                      id="isEvent"
                      label="Sorties"
                      name="isEvent"
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                </ul>
              </li>
              <li>
                <div className="sf-toggle-wrapper">
                  <div>
                    <h4>
                      {'Uniquement les offres duo'}
                    </h4>
                    {offerIsDuoCounter > 0 && (
                      <span className="sf-selected-filter-counter">
                        {`(${offerIsDuoCounter})`}
                      </span>
                    )}
                  </div>
                  <FilterToggle
                    checked={offerIsDuo}
                    id="offerIsDuo"
                    name="offerIsDuo"
                    onChange={this.handleOnToggle}
                  />
                </div>
              </li>
              <li>
                <div className="sf-toggle-wrapper">
                  <div>
                    <h4>
                      {'Uniquement les offres gratuites'}
                    </h4>
                    {offerIsFreeCounter > 0 && (
                      <span className="sf-selected-filter-counter">
                        {`(${offerIsFreeCounter})`}
                      </span>
                    )}
                  </div>
                  <FilterToggle
                    checked={offerIsFree}
                    id="offerIsFree"
                    name="offerIsFree"
                    onChange={this.handleOnToggle}
                  />
                </div>
              </li>
              {!offerIsFree && (
                <li className="sf-price-slider-wrapper">
                  <h4 className="sf-title">
                    {'Prix'}
                  </h4>
                  {priceRangeCounter > 0 && (
                    <span className="sf-selected-filter-counter">
                      {`(${priceRangeCounter})`}
                    </span>
                  )}
                  <span className="sf-slider-indicator">
                    {`${priceRange[0]} € - ${priceRange[1]} €`}
                  </span>
                  <Range
                    allowCross={false}
                    max={500}
                    min={0}
                    onAfterChange={this.handleOffersFetchAndUrlUpdate}
                    onChange={this.handlePriceSlide}
                    value={priceRange}
                  />
                </li>
              )}
              <li>
                <div className="sf-toggle-wrapper">
                  <div>
                    <h4>
                      {'Date'}
                    </h4>
                    {dateFilterCounter > 0 && (
                      <span className="sf-selected-filter-counter">
                        {`(${dateFilterCounter})`}
                      </span>
                    )}
                    <p className="sf-toggle-information">
                      {'Seules les offres Sorties seront affichées'}
                    </p>
                  </div>
                  <FilterToggle
                    checked={isOfferFilteredByDate}
                    id="isOfferFilteredByDate"
                    name="isOfferFilteredByDate"
                    onChange={this.handleDateToggle}
                  />
                </div>
              </li>
              {isOfferFilteredByDate && (
                <li className="sf-date-wrapper">
                  <h4 className="sf-title">
                    {"Date de l'offre"}
                  </h4>
                  <ul>
                    <li>
                      <input
                        id="today"
                        name="dateOption"
                        onChange={this.handleDateSelection}
                        type="radio"
                        value={DATE_FILTER.TODAY.value}
                      />
                      <label
                        className={date.option === DATE_FILTER.TODAY.value && 'sf-filter-checked'}
                        htmlFor="today"
                      >
                        {DATE_FILTER.TODAY.label}
                      </label>
                      {date.option === DATE_FILTER.TODAY.value && <Icon svg="ico-check-pink" />}
                    </li>
                    <li>
                      <input
                        id="current-week"
                        name="dateOption"
                        onChange={this.handleDateSelection}
                        type="radio"
                        value={DATE_FILTER.CURRENT_WEEK.value}
                      />
                      <label
                        className={
                          date.option === DATE_FILTER.CURRENT_WEEK.value && 'sf-filter-checked'
                        }
                        htmlFor="current-week"
                      >
                        {DATE_FILTER.CURRENT_WEEK.label}
                      </label>
                      {date.option === DATE_FILTER.CURRENT_WEEK.value && (
                        <Icon svg="ico-check-pink" />
                      )}
                    </li>
                    <li>
                      <input
                        id="current-week-end"
                        name="dateOption"
                        onChange={this.handleDateSelection}
                        type="radio"
                        value={DATE_FILTER.CURRENT_WEEK_END.value}
                      />
                      <label
                        className={
                          date.option === DATE_FILTER.CURRENT_WEEK_END.value && 'sf-filter-checked'
                        }
                        htmlFor="current-week-end"
                      >
                        {DATE_FILTER.CURRENT_WEEK_END.label}
                      </label>
                      {date.option === DATE_FILTER.CURRENT_WEEK_END.value && (
                        <Icon svg="ico-check-pink" />
                      )}
                    </li>
                    <li>
                      <input
                        id="picked"
                        name="dateOption"
                        onChange={this.handleDateSelection}
                        type="radio"
                        value={DATE_FILTER.USER_PICK.value}
                      />
                      <label
                        className={
                          date.option === DATE_FILTER.USER_PICK.value && 'sf-filter-checked'
                        }
                        htmlFor="picked"
                      >
                        {DATE_FILTER.USER_PICK.label}
                      </label>
                      {date.option === DATE_FILTER.USER_PICK.value && <Icon svg="ico-check-pink" />}
                    </li>
                  </ul>
                  {date.option === DATE_FILTER.USER_PICK.value && (
                    <DatePicker
                      calendarClassName="sf-filter-datepicker"
                      inline
                      minDate={moment(new Date())}
                      onChange={this.handlePickedDate}
                      selected={moment(date.selectedDate)}
                    />
                  )}
                </li>
              )}
              <li className="sf-space-wrapper" />
            </ul>
            <div className="sf-button-wrapper">
              <button
                className="sf-button"
                disabled={nbHits === 0}
                onClick={this.handleFilterOffers}
                type="button"
              >
                {this.buildNumberOfResults()}
              </button>
            </div>
          </Route>
        </Switch>
      </main>
    )
  }
}

Filters.defaultProps = {
  initialFilters: {
    aroundRadius: DEFAULT_RADIUS_IN_KILOMETERS,
    date: null,
    isOfferFilteredByDate: false,
    isSearchAroundMe: false,
    offerCategories: [],
    offerIsDuo: false,
    offerIsFree: false,
    offerTypes: {
      isDigital: false,
      isEvent: false,
      isThing: false,
    },
    priceRange: PRICE_FILTER.DEFAULT_RANGE,
    sortBy: '',
  },
}

Filters.propTypes = {
  geolocation: PropTypes.shape().isRequired,
  history: PropTypes.shape().isRequired,
  initialFilters: PropTypes.shape({
    aroundRadius: PropTypes.number,
    date: PropTypes.instanceOf(Date),
    isOfferFilteredByDate: PropTypes.bool,
    isSearchAroundMe: PropTypes.bool,
    offerCategories: PropTypes.arrayOf(PropTypes.string),
    offerIsDuo: PropTypes.bool,
    offerIsFree: PropTypes.bool,
    offerTypes: PropTypes.shape({
      isDigital: PropTypes.bool,
      isEvent: PropTypes.bool,
      isThing: PropTypes.bool,
    }),
    priceRange: PropTypes.arrayOf(PropTypes.number),
    sortBy: PropTypes.string,
  }),
  match: PropTypes.shape().isRequired,
  offers: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  showFailModal: PropTypes.func.isRequired,
  updateFilteredOffers: PropTypes.func.isRequired,
  updateFilters: PropTypes.func.isRequired,
  updateNumberOfActiveFilters: PropTypes.func.isRequired,
}
