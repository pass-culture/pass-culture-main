import PropTypes from 'prop-types'
import Slider, { Range } from 'rc-slider'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from '../Criteria/criteriaEnums'
import CriteriaLocation from '../CriteriaLocation/CriteriaLocation'
import { checkIfSearchAround } from '../utils/checkIfSearchAround'
import Checkbox from './Checkbox/Checkbox'
import { RadioList } from './RadioList/RadioList'
import { DATE_FILTER, PRICE_FILTER } from './filtersEnums'
import Toggle from './Toggle/Toggle'
import { DEFAULT_RADIUS_IN_KILOMETERS } from '../../../../vendor/algolia/filters'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import { buildPlaceLabel } from '../CriteriaLocation/utils/buildPlaceLabel'

export class Filters extends PureComponent {
  constructor(props) {
    super(props)
    const {
      aroundRadius,
      date,
      offerIsFilteredByDate,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      searchAround,
      sortBy,
    } = props.initialFilters
    const offerCategories = this.buildCategoriesStateFromProps()
    this.state = {
      areCategoriesVisible: true,
      filters: {
        aroundRadius,
        date,
        offerIsFilteredByDate,
        offerCategories,
        offerIsFree,
        offerIsDuo,
        offerTypes,
        priceRange,
        searchAround,
        sortBy,
      },
      place: props.place,
      userGeolocation: props.userGeolocation
    }
    this.radioListRef = React.createRef()
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
                   keywords,
                   offerCategories,
                   offerIsDuo,
                   offerIsFree,
                   offerTypes,
                   priceRange,
                   searchAround,
                   sortBy,
                 }) => {
    const { showFailModal, updateFilteredOffers } = this.props
    const searchAroundUserOrPlace = !searchAround.everywhere

    fetchAlgolia({
      aroundRadius,
      date,
      geolocation,
      keywords,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      searchAround: searchAroundUserOrPlace,
      sortBy,
    })
      .then(offers => {
        updateFilteredOffers(offers)
      })
      .catch(() => {
        showFailModal()
      })
  }

  handleOffersFetchAndUrlUpdate = () => {
    const { history, query } = this.props
    const { filters, place, userGeolocation } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    const {
      aroundRadius,
      date,
      offerIsFilteredByDate,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      searchAround,
      sortBy,
    } = filters
    const offerCategories = this.getSelectedCategories()
    const dateFilter = offerIsFilteredByDate ? date : null

    this.fetchOffers({
      aroundRadius,
      date: dateFilter,
      geolocation: searchAround.place ? place.geolocation : userGeolocation,
      keywords,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      searchAround,
      sortBy,
    })

    const search = this.buildSearchParameter()
    history.replace({ search })
  }

  buildSearchParameter = () => {
    const { filters, place, userGeolocation } = this.state
    const { query } = this.props
    const { searchAround, sortBy } = filters
    const offerCategories = this.getSelectedCategories()
    const autourDe = checkIfSearchAround(searchAround)
    const categories = offerCategories.join(';') || ''
    const tri = sortBy
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    return `?mots-cles=${keywords}` +
      `&autour-de=${autourDe}&tri=${tri}&categories=${categories}` +
      `&latitude=${searchAround.place ? place.geolocation.latitude : userGeolocation.latitude}` +
      `&longitude=${searchAround.place ? place.geolocation.longitude : userGeolocation.longitude}` +
      `${searchAround.place ? `&place=${place.name.long}` : ''}`
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
          offerIsFilteredByDate: false,
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: {
            everywhere: true,
            place: false,
            user: false
          }
        },
        place: null
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
    const { offers: { nbHits } } = this.props

    if (nbHits === 0) {
      return 'Aucun résultat'
    }

    const results = nbHits < 1000 ? `${nbHits}` : `999+`
    return `Afficher les ${results} résultats`
  }

  buildGeolocationFilter = () => {
    const { filters: { searchAround }, place }  = this.state

    if (searchAround.everywhere) return 'Partout'
    if (searchAround.place) return buildPlaceLabel(place)
    if (searchAround.user) return 'Autour de moi'
  }

  getActiveCriterionLabel = () => {
    const { query } = this.props
    const queryParams = query.parse()
    const place = queryParams['place'] || ''
    const { filters: { searchAround } } = this.state

    if (searchAround.everywhere) return GEOLOCATION_CRITERIA.EVERYWHERE.label
    if (searchAround.place) return place
    if (searchAround.user) return GEOLOCATION_CRITERIA.AROUND_ME.label
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

  getPriceRangeCounter = (priceRange) => {
    const [lowestPrice, highestPrice] = priceRange
    const [defaultLowestPrice, defaultHighestPrice] = PRICE_FILTER.DEFAULT_RANGE
    return lowestPrice !== defaultLowestPrice || highestPrice !== defaultHighestPrice ? 1 : 0
  }

  getNumberFromBoolean = boolean => (boolean === true ? 1 : 0)

  getNumberFromSearchAround = searchAround => {
    if (searchAround.user || searchAround.place) {
      return 1
    }
    return 0
  }

  handleGeolocationCriterionSelection = criterionKey => {
    const { filters } = this.state
    const { history } = this.props

    const isSearchEverywhere = GEOLOCATION_CRITERIA[criterionKey].label === GEOLOCATION_CRITERIA.EVERYWHERE.label
    const isSearchAroundUser = GEOLOCATION_CRITERIA[criterionKey].label === GEOLOCATION_CRITERIA.AROUND_ME.label
    const isSearchAroundPlace = !isSearchEverywhere && !isSearchAroundUser
    this.setState(
      {
        filters: {
          ...filters,
          searchAround: {
            everywhere: isSearchEverywhere,
            place: isSearchAroundPlace,
            user: isSearchAroundUser,
          }
        },
        place: null
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
        const search = this.buildSearchParameter()
        history.push(`/recherche/resultats/filtres${search}`)
      }
    )
  }

  handleOnPlaceSelection = place => {
    const { filters } = this.state
    this.setState({
      filters: {
        ...filters,
        searchAround: {
          everywhere: false,
          place: true,
          user: false
        },
      },
      place
    }, () => {
      this.handleOffersFetchAndUrlUpdate()
    })
  }

  handleGoToGeolocationFilter = () => {
    const { history } = this.props
    const {
      location: { search = '' },
    } = history
    history.push(`/recherche/resultats/filtres/localisation${search}`)
  }

  handleFilterOffers = () => {
    const { history, updateFilters, updateNumberOfActiveFilters, updatePlace } = this.props
    const {
      location: { search = '' },
    } = history
    const { filters, place } = this.state
    const {
      offerIsFilteredByDate,
      offerCategories,
      offerTypes,
      offerIsDuo,
      offerIsFree,
      priceRange,
      searchAround
    } = filters
    const updatedFilters = { ...filters }
    updatedFilters.offerCategories = this.getSelectedCategories()
    const geolocationFilterCounter = this.getNumberFromSearchAround(searchAround)
    const offerTypesFilterCounter = this.getNumberOfSelectedFilters(offerTypes)
    const offerCategoriesFilterCounter = this.getNumberOfSelectedFilters(offerCategories)
    const offerIsDuoFilterCounter = this.getNumberFromBoolean(offerIsDuo)
    const offerIsFreeFilterCounter = this.getNumberFromBoolean(offerIsFree)
    const priceRangeFilterCounter = this.getPriceRangeCounter(priceRange)
    const dateFilterCounter = this.getNumberFromBoolean(offerIsFilteredByDate)
    const numberOfActiveFilters =
      offerTypesFilterCounter +
      offerCategoriesFilterCounter +
      geolocationFilterCounter +
      offerIsDuoFilterCounter +
      offerIsFreeFilterCounter +
      priceRangeFilterCounter +
      dateFilterCounter
    updateFilters(updatedFilters)
    updateNumberOfActiveFilters(numberOfActiveFilters)
    updatePlace(place)
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
          offerIsFilteredByDate: checked,
          date: {
            ...filters.date,
            selectedDate: new Date(),
          },
        },
      },
      () => {
        this.handleOffersFetchAndUrlUpdate()
        const { filters: filtersAfterUpdate } = this.state
        if (filtersAfterUpdate.offerIsFilteredByDate) {
          this.radioListRef.current.scrollIntoView()
        }
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
        this.radioListRef.current.scrollIntoView()
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
    const { offers: { nbHits } } = this.props
    const { areCategoriesVisible, filters, place } = this.state
    const {
      aroundRadius,
      date,
      offerIsFilteredByDate,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      searchAround
    } = filters
    const { history, match, userGeolocation } = this.props
    const { location } = history
    const { search = '' } = location
    const numberOfOfferTypesSelected = this.getNumberOfSelectedFilters(offerTypes)
    const numberOfOfferCategoriesSelected = this.getNumberOfSelectedFilters(offerCategories)
    const geolocationFilterCounter = this.getNumberFromSearchAround(searchAround)
    const offerIsDuoCounter = this.getNumberFromBoolean(offerIsDuo)
    const offerIsFreeCounter = this.getNumberFromBoolean(offerIsFree)
    const priceRangeCounter = this.getPriceRangeCounter(priceRange)
    const dateFilterCounter = this.getNumberFromBoolean(offerIsFilteredByDate)

    return (
      <main className="search-filters-page">
        <Switch>
          <Route path="/recherche/resultats/filtres/localisation">
            <CriteriaLocation
              activeCriterionLabel={this.getActiveCriterionLabel()}
              backTo={`/recherche/resultats/filtres${search}`}
              criteria={GEOLOCATION_CRITERIA}
              geolocation={userGeolocation}
              history={history}
              match={match}
              onCriterionSelection={this.handleGeolocationCriterionSelection}
              onPlaceSelection={this.handleOnPlaceSelection}
              place={place}
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
                {(searchAround.user || searchAround.place) && (
                  <span className="sf-warning-message">
                    {'Seules les offres Sorties et Physiques seront affichées'}
                  </span>
                )}
                <span className="sf-filter-separator" />
              </li>
              {(searchAround.user || searchAround.place) && (
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
                            <Checkbox
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
                    {'Type d\'offres'}
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
                    <Checkbox
                      checked={offerTypes.isDigital}
                      className={`${offerTypes.isDigital ? 'fc-label-checked' : 'fc-label'}`}
                      id="isDigital"
                      label="Offres numériques"
                      name="isDigital"
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                  <li>
                    <Checkbox
                      checked={offerTypes.isThing}
                      className={`${offerTypes.isThing ? 'fc-label-checked' : 'fc-label'}`}
                      id="isThing"
                      label="Offres physiques"
                      name="isThing"
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                  <li>
                    <Checkbox
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
                  <Toggle
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
                  <Toggle
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
                  <Toggle
                    checked={offerIsFilteredByDate}
                    id="offerIsFilteredByDate"
                    name="offerIsFilteredByDate"
                    onChange={this.handleDateToggle}
                  />
                </div>
              </li>
              {offerIsFilteredByDate && (
                <RadioList
                  date={date}
                  onDateSelection={this.handleDateSelection}
                  onPickedDate={this.handlePickedDate}
                  ref={this.radioListRef}
                />
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
    offerIsFilteredByDate: false,
    offerCategories: [],
    offerIsDuo: false,
    offerIsFree: false,
    offerTypes: {
      isDigital: false,
      isEvent: false,
      isThing: false,
    },
    priceRange: PRICE_FILTER.DEFAULT_RANGE,
    searchAround: {
      everywhere: true,
      place: false,
      user: false
    },
    sortBy: '',
  },
  place: {
    geolocation: { latitude: null, longitude: null },
    name: null
  }
}

Filters.propTypes = {
  history: PropTypes.shape().isRequired,
  initialFilters: PropTypes.shape({
    aroundRadius: PropTypes.number,
    date: PropTypes.shape({
      option: PropTypes.string,
      selectedDate: PropTypes.instanceOf(Date),
    }),
    offerIsFilteredByDate: PropTypes.bool,
    offerCategories: PropTypes.arrayOf(PropTypes.string),
    offerIsDuo: PropTypes.bool,
    offerIsFree: PropTypes.bool,
    offerTypes: PropTypes.shape({
      isDigital: PropTypes.bool,
      isEvent: PropTypes.bool,
      isThing: PropTypes.bool,
    }),
    priceRange: PropTypes.arrayOf(PropTypes.number),
    searchAround: PropTypes.shape({
      everywhere: PropTypes.bool,
      place: PropTypes.bool,
      user: PropTypes.bool,
    }),
    sortBy: PropTypes.string,
  }),
  match: PropTypes.shape().isRequired,
  offers: PropTypes.shape().isRequired,
  place: PropTypes.shape({
    geolocation: PropTypes.shape({
      latitude: PropTypes.number,
      longitude: PropTypes.number,
    }),
    name: PropTypes.shape({
      long: PropTypes.string,
      short: PropTypes.string,
    })
  }),
  query: PropTypes.shape().isRequired,
  showFailModal: PropTypes.func.isRequired,
  updateFilteredOffers: PropTypes.func.isRequired,
  updateFilters: PropTypes.func.isRequired,
  updateNumberOfActiveFilters: PropTypes.func.isRequired,
  updatePlace: PropTypes.func.isRequired,
  userGeolocation: PropTypes.shape().isRequired,
}
