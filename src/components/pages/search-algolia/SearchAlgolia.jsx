import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { SearchCriteria } from './Criteria/SearchCriteria'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from './Criteria/searchCriteriaValues'
import { SearchHome } from './Home/SearchHome'
import SearchResults from './Result/SearchResults'

const GEOLOCATION_ACTIVATION_REQUEST =
  'Veuillez activer la géolocalisation pour voir les offres autour de vous.'

class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      geolocationCriterion: {
        isSearchAroundMe: props.isGeolocationEnabled(),
        params: props.isGeolocationEnabled()
          ? GEOLOCATION_CRITERIA.AROUND_ME
          : GEOLOCATION_CRITERIA.EVERYWHERE,
      },
      categoryCriterion: CATEGORY_CRITERIA.ALL,
    }
  }

  handleGeolocationCriterionSelection = criterionKey => () => {
    const { isGeolocationEnabled } = this.props
    if (GEOLOCATION_CRITERIA[criterionKey].requiresGeolocation && !isGeolocationEnabled()) {
      return window.alert(GEOLOCATION_ACTIVATION_REQUEST)
    }

    const label = GEOLOCATION_CRITERIA[criterionKey].label
    this.setState(() => {
      return {
        geolocationCriterion: {
          isSearchAroundMe: label === GEOLOCATION_CRITERIA.AROUND_ME.label,
          params: GEOLOCATION_CRITERIA[criterionKey],
        },
      }
    })
    const { redirectToSearchMainPage } = this.props
    redirectToSearchMainPage()
  }

  handleCategoryCriterionSelection = criterionKey => () => {
    this.setState(() => ({
      categoryCriterion: CATEGORY_CRITERIA[criterionKey],
    }))
    const { redirectToSearchMainPage } = this.props
    redirectToSearchMainPage()
  }

  render() {
    const {
      location,
      match,
      query,
      redirectToSearchMainPage,
      history,
      geolocation,
      isGeolocationEnabled,
    } = this.props
    const { geolocationCriterion, categoryCriterion } = this.state

    return (
      <Switch>
        <Route
          exact
          path="/recherche-offres(/menu)?"
        >
          <SearchHome
            categoryCriterion={categoryCriterion}
            geolocationCriterion={geolocationCriterion}
            history={history}
          />
        </Route>
        <Route path="/recherche-offres/resultats">
          <SearchResults
            categoriesFilter={categoryCriterion.filters}
            geolocation={geolocation}
            isSearchAroundMe={geolocationCriterion.isSearchAroundMe}
            location={location}
            match={match}
            query={query}
            redirectToSearchMainPage={redirectToSearchMainPage}
          />
        </Route>
        <Route path="/recherche-offres/criteres-localisation">
          <SearchCriteria
            activeCriterionLabel={geolocationCriterion.params.label}
            criteria={GEOLOCATION_CRITERIA}
            history={history}
            isGeolocationEnabled={isGeolocationEnabled}
            location={location}
            match={match}
            onCriterionSelection={this.handleGeolocationCriterionSelection}
            title="Localisation"
          />
        </Route>
        <Route path="/recherche-offres/criteres-categorie">
          <SearchCriteria
            activeCriterionLabel={categoryCriterion.label}
            criteria={CATEGORY_CRITERIA}
            history={history}
            location={location}
            match={match}
            onCriterionSelection={this.handleCategoryCriterionSelection}
            title="Catégories"
          />
        </Route>
      </Switch>
    )
  }
}

SearchAlgolia.defaultProps = {
  geolocation: {},
}

SearchAlgolia.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  history: PropTypes.shape({ push: PropTypes.func }).isRequired,
  isGeolocationEnabled: PropTypes.func.isRequired,
  location: PropTypes.shape({
    search: PropTypes.string,
  }).isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
}

export default SearchAlgolia
