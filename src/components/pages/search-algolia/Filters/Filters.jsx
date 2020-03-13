import React, { PureComponent } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import PropTypes from 'prop-types'
import { Criteria } from '../Criteria/Criteria'
import { Route, Switch } from 'react-router'
import { GEOLOCATION_CRITERIA } from '../Criteria/criteriaEnums'
import { checkIfAroundMe } from '../utils/checkIfAroundMe'

export class Filters extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      currentFilters: {
        categories: props.initialFilters.categories,
        isSearchAroundMe: props.initialFilters.isSearchAroundMe,
        sortCriteria: props.initialFilters.sortCriteria
      },
      initialFilters: {
        categories: props.initialFilters.categories,
        isSearchAroundMe: props.initialFilters.isSearchAroundMe,
        sortCriteria: props.initialFilters.sortCriteria
      },
      offers: props.offers
    }
  }

  fetchOffers = (keywords, geolocation = null, categories, indexSuffix) => {
    const { showFailModal } = this.props
    fetchAlgolia(keywords, 0, geolocation, categories, indexSuffix)
      .then(offers => {
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
    const { currentFilters } = this.state

    if (!isUserAllowedToSelectCriterion(criterionKey, isGeolocationEnabled)) return

    this.setState({
      currentFilters: {
        ...currentFilters,
        isSearchAroundMe: GEOLOCATION_CRITERIA[criterionKey].label === GEOLOCATION_CRITERIA.AROUND_ME.label
      }
    }, () => {
      this.process()
      redirectToSearchFiltersPage()
    })
  }

  resetFilters = () => {
    const { initialFilters } = this.state

    this.setState({
      currentFilters: {
        ...initialFilters
      },
    }, () => {
      this.process()
    })
  }

  process = () => {
    const { history, geolocation, query } = this.props
    const { currentFilters } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    const { categories, isSearchAroundMe, sortCriteria} = currentFilters
    isSearchAroundMe ?
      this.fetchOffers(keywords, geolocation, categories, sortCriteria) :
      this.fetchOffers(keywords, null, categories, sortCriteria)

    const autourDeMoi = checkIfAroundMe(currentFilters.isSearchAroundMe)
    const category = currentFilters.categories !== '' ? currentFilters.categories.join(';') : ''
    const tri = currentFilters.sortCriteria
    history.replace({
      search: `?mots-cles=${keywords}&autour-de-moi=${autourDeMoi}&tri=${tri}&categories=${category}`
    })
  }

  handleFilterOffers = () => {
    const { history, getFilteredOffers } = this.props
    const { location: { search = '' } } = history
    const { offers } = this.state
    getFilteredOffers(offers)
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
    const { currentFilters } = this.state
    return currentFilters.isSearchAroundMe ? 'Autour de moi' : 'Partout'
  }

  getActiveCriterionLabel = () => {
    const { currentFilters } = this.state
    return currentFilters.isSearchAroundMe ? GEOLOCATION_CRITERIA.AROUND_ME.label : GEOLOCATION_CRITERIA.EVERYWHERE.label
  }

  render() {
    const { history, match } = this.props
    const { location } = history
    const { search = '' } = location

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
              </li>
              <div className="sf-filter-separator" />
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
  getFilteredOffers: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  initialFilters: PropTypes.shape(),
  isGeolocationEnabled: PropTypes.bool.isRequired,
  isUserAllowedToSelectCriterion: PropTypes.func.isRequired,
  match: PropTypes.shape().isRequired,
  offers: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  redirectToSearchFiltersPage: PropTypes.func.isRequired,
  showFailModal: PropTypes.func.isRequired
}
