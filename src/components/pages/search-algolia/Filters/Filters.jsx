import React, { PureComponent } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import PropTypes from 'prop-types'
import { Criteria } from '../Criteria/Criteria'
import { Route, Switch } from 'react-router'
import { GEOLOCATION_CRITERIA } from '../Criteria/criteriaEnums'
import { checkIfAroundMe } from '../utils/checkIfAroundMe'
import FilterCheckbox from './FilterCheckbox/FilterCheckbox'

export class Filters extends PureComponent {
  constructor(props) {
    super(props)

    const { categories, isSearchAroundMe, offerTypes, sortCriteria } = props.initialFilters
    this.state = {
      filters: {
        categories: categories,
        isSearchAroundMe: isSearchAroundMe,
        offerTypes: offerTypes,
        sortCriteria: sortCriteria
      },
      offers: props.offers
    }
  }

  fetchOffers = ({ keywords, geolocation = null, categories, indexSuffix, offerTypes }) => {
    const { showFailModal } = this.props
    fetchAlgolia({
      categories,
      geolocationCoordinates: geolocation,
      indexSuffix,
      keywords,
      offerTypes,
      page: 0
    }).then(offers => {
      this.setState({
        offers: offers
      })
    })
      .catch(() => {
        showFailModal()
      })
  }

  handleGeolocationCriterionSelection = criterionKey => () => {
    const {
      isUserAllowedToSelectCriterion,
      isGeolocationEnabled,
      redirectToSearchFiltersPage
    } = this.props
    const { filters } = this.state

    if (!isUserAllowedToSelectCriterion(criterionKey, isGeolocationEnabled)) return

    this.setState({
      filters: {
        ...filters,
        isSearchAroundMe: GEOLOCATION_CRITERIA[criterionKey].label === GEOLOCATION_CRITERIA.AROUND_ME.label
      }
    }, () => {
      this.process()
      redirectToSearchFiltersPage()
    })
  }

  resetFilters = () => {
    const { initialFilters } = this.props

    this.setState({
      filters: {
        ...initialFilters,
        offerTypes: {
          isDigital: false
        }
      },
    }, () => {
      this.process()
    })
  }

  process = () => {
    const { history, geolocation, query } = this.props
    const { filters } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    const { categories, isSearchAroundMe, offerTypes, sortCriteria } = filters
    isSearchAroundMe ?
      this.fetchOffers({ keywords, geolocation, categories, indexSuffix: sortCriteria, offerTypes }) :
      this.fetchOffers({ keywords, categories, indexSuffix: sortCriteria, offerTypes })

    const autourDeMoi = checkIfAroundMe(filters.isSearchAroundMe)
    const category = filters.categories !== '' ? filters.categories.join(';') : ''
    const tri = filters.sortCriteria
    history.replace({
      search: `?mots-cles=${keywords}&autour-de-moi=${autourDeMoi}&tri=${tri}&categories=${category}`
    })
  }

  handleFilterOffers = () => {
    const { history, updateFilteredOffers, updateFilters } = this.props
    const { location: { search = '' } } = history
    const { filters, offers } = this.state

    updateFilters(filters)
    updateFilteredOffers(offers)
    history.push(`/recherche-offres/resultats${search}`)
  }

  handleToGeolocationFilter = () => {
    const { history } = this.props
    const { location: { search = '' } } = history
    history.push(`/recherche-offres/resultats/filtres/localisation${search}`)
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
    return filters.isSearchAroundMe ? GEOLOCATION_CRITERIA.AROUND_ME.label : GEOLOCATION_CRITERIA.EVERYWHERE.label
  }

  handleOnChange = event => {
    const { name, checked } = event.target
    const { filters } = this.state

    this.setState({
      filters: {
        ...filters,
        offerTypes: {
          [name]: checked
        }
      }
    }, () => {
      this.process()
    })
  }

  getNumberOfOfferTypesSelected = () => {
    const { filters } = this.state
    const { offerTypes } = filters
    let counter = 0

    Object.keys(offerTypes).forEach((key) => {
       if (offerTypes[key] === true){
         counter++
       }
    })
    return counter
  }

  render() {
    const { filters } = this.state
    const { offerTypes } = filters
    const { history, match } = this.props
    const { location } = history
    const { search = '' } = location
    const numberOfOfferTypesSelected = this.getNumberOfOfferTypesSelected()

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
                <h4 className='sf-geolocation-title'>
                  {'Localisation'}
                </h4>
                <button
                  className="sf-geolocation-button"
                  onClick={this.handleToGeolocationFilter}
                  type="button"
                >
                  {this.buildGeolocationFilter()}
                </button>
                <div className="sf-filter-separator" />
              </li>
              <li>
                <h4 className='sf-offer-type-title'>
                  {'Type d\'offre'}
                </h4>
                {numberOfOfferTypesSelected > 0 && (
                  <span className='sf-offer-type-counter'>
                      {`(${numberOfOfferTypesSelected})`}
                  </span>
                )}
                <div className='sf-offer-type-wrapper'>
                  <FilterCheckbox
                    checked={offerTypes.isDigital}
                    className={`${offerTypes.isDigital ? 'fc-label-checked' : 'fc-label'}`}
                    id='isDigital'
                    label='Offres numériques'
                    name='isDigital'
                    onChange={this.handleOnChange}
                  />
                </div>
                <div className="sf-filter-separator" />
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
    isSearchAroundMe: false
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
  updateFilters: PropTypes.func.isRequired
}
