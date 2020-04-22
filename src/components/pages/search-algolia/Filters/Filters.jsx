//radiusRevert:
/* eslint-disable no-unused-vars */

import PropTypes from 'prop-types'
import { Range } from 'rc-slider'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import { Criteria } from '../Criteria/Criteria'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from '../Criteria/criteriaEnums'
import { checkIfAroundMe } from '../utils/checkIfAroundMe'
import FilterCheckbox from './FilterCheckbox/FilterCheckbox'
import FilterToggle from './FilterToggle/FilterToggle'

export class Filters extends PureComponent {
  constructor(props) {
    super(props)

    const {
      aroundRadius,
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
    keywords,
    geolocation,
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
      geolocation,
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

    const { aroundRadius, offerIsDuo, offerIsFree, offerTypes, priceRange, sortBy } = filters
    const offerCategories = this.getSelectedCategories()

    this.fetchOffers({
      //revert aroundRadius,
      keywords,
      geolocation,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      sortBy,
    })

    const autourDeMoi = checkIfAroundMe(filters.isSearchAroundMe)
    const categories = offerCategories.join(';') || ''
    const tri = sortBy
    history.replace({
      search: `?mots-cles=${keywords}&autour-de-moi=${autourDeMoi}&tri=${tri}&categories=${categories}`,
    })
  }

  resetFilters = () => {
    const { initialFilters } = this.props

    this.setState(
      {
        filters: {
          ...initialFilters,
          isSearchAroundMe: false,
          //radiusRevert: aroundRadius: 0,
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: [0, 500],
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
    const [defaultLowestPrice, defaultHighestPrice] = [0, 500]
    return lowestPrice !== defaultLowestPrice || highestPrice !== defaultHighestPrice ? 1 : 0
  }

  getNumberFromBoolean = boolean => (boolean === true ? 1 : 0)

  handleGeolocationCriterionSelection = criterionKey => () => {
    const {
      isUserAllowedToSelectCriterion,
      isGeolocationEnabled,
      redirectToSearchFiltersPage,
    } = this.props
    const { filters } = this.state

    if (!isUserAllowedToSelectCriterion(criterionKey, isGeolocationEnabled)) return

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
        redirectToSearchFiltersPage()
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
    const { nbHits } = offers
    const {
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
    const numberOfActiveFilters =
      offerTypesFilterCounter +
      offerCategoriesFilterCounter +
      geolocationFilterCounter +
      offerIsDuoFilterCounter +
      offerIsFreeFilterCounter +
      priceRangeFilterCounter

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

  render() {
    const { areCategoriesVisible, filters, offers } = this.state
    const { nbHits } = offers
    const {
      aroundRadius,
      isSearchAroundMe,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
    } = filters
    const { history, match } = this.props
    const { location } = history
    const { search = '' } = location
    const numberOfOfferTypesSelected = this.getNumberOfSelectedFilters(offerTypes)
    const numberOfOfferCategoriesSelected = this.getNumberOfSelectedFilters(offerCategories)
    const geolocationFilterCounter = this.getNumberFromBoolean(isSearchAroundMe)
    const offerIsDuoCounter = this.getNumberFromBoolean(offerIsDuo)
    const offerIsFreeCounter = this.getNumberFromBoolean(offerIsFree)
    const priceRangeCounter = this.getPriceRangeCounter(priceRange)

    return (
      <main className="search-filters-page">
        <Switch>
          <Route path="/recherche/resultats/filtres/localisation">
            <Criteria
              activeCriterionLabel={this.getActiveCriterionLabel()}
              backTo={`/recherche/resultats/filtres${search}`}
              criteria={GEOLOCATION_CRITERIA}
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
                <span className="sf-filter-separator" />
              </li>
              {/*//radiusRevert:{isSearchAroundMe && (*/}
              {/*  <li>*/}
              {/*    <h4 className="sf-title">*/}
              {/*      {'Rayon'}*/}
              {/*    </h4>*/}
              {/*    <h4 className="sf-slider-indicator">*/}
              {/*      {`${aroundRadius} km`}*/}
              {/*    </h4>*/}
              {/*    <div className="sf-slider-wrapper">*/}
              {/*      <Slider*/}
              {/*        max={100}*/}
              {/*        min={0}*/}
              {/*        onAfterChange={this.handleRadiusAfterSlide}*/}
              {/*        onChange={this.handleRadiusSlide}*/}
              {/*        value={aroundRadius}*/}
              {/*      />*/}
              {/*    </div>*/}
              {/*    <span className="sf-filter-separator" />*/}
              {/*  </li>*/}
              {/*)}*/}
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
                <div className="sf-offer-price-wrapper">
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
                <div className="sf-offer-price-wrapper">
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
    // revert-to-include -> aroundRadius: 100,
    isSearchAroundMe: false,
    offerCategories: [],
    offerIsDuo: false,
    offerIsFree: false,
    offerTypes: {
      isDigital: false,
      isEvent: false,
      isThing: false,
    },
    priceRange: [0, 500],
    sortBy: '',
  },
}

Filters.propTypes = {
  geolocation: PropTypes.shape().isRequired,
  history: PropTypes.shape().isRequired,
  initialFilters: PropTypes.shape({
    aroundRadius: PropTypes.number,
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
  isGeolocationEnabled: PropTypes.bool.isRequired,
  isUserAllowedToSelectCriterion: PropTypes.func.isRequired,
  match: PropTypes.shape().isRequired,
  offers: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  redirectToSearchFiltersPage: PropTypes.func.isRequired,
  showFailModal: PropTypes.func.isRequired,
  updateFilteredOffers: PropTypes.func.isRequired,
  updateFilters: PropTypes.func.isRequired,
  updateNumberOfActiveFilters: PropTypes.func.isRequired,
}
