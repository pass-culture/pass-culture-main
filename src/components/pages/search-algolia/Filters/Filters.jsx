import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import { Criteria } from '../Criteria/Criteria'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from '../Criteria/criteriaEnums'
import { checkIfAroundMe } from '../utils/checkIfAroundMe'
import FilterCheckbox from './FilterCheckbox/FilterCheckbox'
import Slider from 'rc-slider'

export class Filters extends PureComponent {
  constructor(props) {
    super(props)

    const { aroundRadius, isSearchAroundMe, offerTypes, sortBy } = props.initialFilters
    this.state = {
      areCategoriesVisible: true,
      filters: {
        aroundRadius: aroundRadius,
        isSearchAroundMe: isSearchAroundMe,
        offerCategories: this.buildCategoriesStateFromProps(),
        offerTypes: offerTypes,
        sortBy: sortBy,
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

  fetchOffers = ({ aroundRadius, keywords, geolocation, offerCategories, offerTypes, sortBy }) => {
    const { showFailModal } = this.props
    fetchAlgolia({
      aroundRadius,
      geolocation,
      keywords,
      offerCategories,
      offerTypes,
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

  process = () => {
    const { history, geolocation, query } = this.props
    const { filters } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    const { aroundRadius, isSearchAroundMe, offerTypes, sortBy } = filters
    const offerCategories = this.getSelectedCategories()

    isSearchAroundMe ?
      this.fetchOffers({
        aroundRadius,
        keywords,
        geolocation,
        offerCategories,
        offerTypes,
        sortBy,
      })
      : this.fetchOffers({
        keywords,
        offerCategories,
        offerTypes,
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

    this.setState({
      filters: {
        ...initialFilters,
        aroundRadius: 0,
        offerCategories: this.buildCategoriesStateFromProps(),
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false
        }
      },
    }, () => {
      this.process()
    })
  }

  getSelectedCategories = () => {
    const { filters } = this.state
    const { offerCategories } = filters

    return Object.keys(offerCategories).filter(categoryKey => offerCategories[categoryKey])
  }

  buildNumberOfResults = () => {
    const { offers } = this.state
    const { nbHits } = offers
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
          isSearchAroundMe: GEOLOCATION_CRITERIA[criterionKey].label === GEOLOCATION_CRITERIA.AROUND_ME.label
        },
      },
      () => {
        this.process()
        redirectToSearchFiltersPage()
      }
    )
  }

  handleToGeolocationFilter = () => {
    const { history } = this.props
    const {
      location: { search = '' },
    } = history
    history.push(`/recherche-offres/resultats/filtres/localisation${search}`)
  }

  handleFilterOffers = () => {
    const { history, updateFilteredOffers, updateFilters } = this.props
    const {
      location: { search = '' },
    } = history
    const { filters, offers } = this.state
    const updatedFilters = { ...filters }
    updatedFilters.offerCategories = this.getSelectedCategories()

    updateFilters(updatedFilters)
    updateFilteredOffers(offers)
    history.push(`/recherche-offres/resultats${search}`)
  }

  handleOnTypeChange = event => {
    const { name, checked } = event.target
    const { filters } = this.state
    const { offerTypes } = filters

    this.setState({
      filters: {
        ...filters,
        offerTypes: {
          ...offerTypes,
          [name]: checked,
        },
      },
    }, () => {
      this.process()
    })
  }

  handleOnCategoryChange = event => {
    const { name, checked } = event.target
    const { filters } = this.state

    this.setState({
      filters: {
        ...filters,
        offerCategories: {
          ...filters.offerCategories,
          [name]: checked,
        },
      },
    }, () => {
      this.process()
    })
  }

  handleToggleCategories = () => () => {
    this.setState(prevState => ({ areCategoriesVisible: !prevState.areCategoriesVisible }))
  }

  handleRadiusSlide = (value) => {
    const { filters } = this.state

    this.setState({
      filters: {
        ...filters,
        aroundRadius: value
      },
    })
  }

  handleRadiusAfterSlide = () => {
    this.process()
  }

  render() {
    const { areCategoriesVisible, filters } = this.state
    const { aroundRadius, isSearchAroundMe, offerCategories, offerTypes } = filters
    const { history, match } = this.props
    const { location } = history
    const { search = '' } = location
    const numberOfOfferTypesSelected = this.getNumberOfSelectedFilters(offerTypes)
    const numberOfOfferCategoriesSelected = this.getNumberOfSelectedFilters(offerCategories)

    return (
      <main className="search-filters-page">
        <Switch>
          <Route path="/recherche-offres/resultats/filtres/localisation">
            <Criteria
              activeCriterionLabel={this.getActiveCriterionLabel()}
              backTo={`/recherche-offres/resultats/filtres${search}`}
              criteria={GEOLOCATION_CRITERIA}
              history={history}
              match={match}
              onCriterionSelection={this.handleGeolocationCriterionSelection}
              title="Localisation"
            />
          </Route>
          <Route path="/recherche-offres/resultats/filtres">
            <div className="sf-header-wrapper">
              <HeaderContainer
                backTo={`/recherche-offres/resultats${search}`}
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
                <button
                  className="sf-geolocation-button"
                  onClick={this.handleToGeolocationFilter}
                  type="button"
                >
                  {this.buildGeolocationFilter()}
                </button>
                <span className="sf-filter-separator" />
              </li>
              {isSearchAroundMe && (
                <li>
                  <h4 className="sf-title">
                    {'Rayon'}
                  </h4>
                  <h4 className="sf-slider-radius">
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
                      id='isThing'
                      label='Offres physiques'
                      name='isThing'
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                  <li>
                    <FilterCheckbox
                      checked={offerTypes.isEvent}
                      className={`${offerTypes.isEvent ? 'fc-label-checked' : 'fc-label'}`}
                      id='isEvent'
                      label='Sorties'
                      name='isEvent'
                      onChange={this.handleOnTypeChange}
                    />
                  </li>
                </ul>
              </li>
            </ul>
            <div className="sf-button-wrapper">
              <button
                className="sf-button"
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
    isSearchAroundMe: false,
    offerCategories: [],
  },
}

Filters.propTypes = {
  geolocation: PropTypes.shape().isRequired,
  history: PropTypes.shape().isRequired,
  initialFilters: PropTypes.shape(),
  isGeolocationEnabled: PropTypes.bool.isRequired,
  isUserAllowedToSelectCriterion: PropTypes.func.isRequired,
  match: PropTypes.shape().isRequired,
  offers: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  redirectToSearchFiltersPage: PropTypes.func.isRequired,
  showFailModal: PropTypes.func.isRequired,
  updateFilteredOffers: PropTypes.func.isRequired,
  updateFilters: PropTypes.func.isRequired,
}
