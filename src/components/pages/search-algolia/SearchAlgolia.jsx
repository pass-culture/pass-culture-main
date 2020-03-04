import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import CategoryCriteria from './Criteria/CategoryCriteria'
import GeolocationCriteria from './Criteria/GeolocationCriteria'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from './Criteria/searchCriteriaValues'
import { SearchHome } from './Home/SearchHome'
import SearchResults from './Result/SearchResults'

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

  handleGeolocationCriterionSelection = criterionKey => {
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

  handleCategoryCriterionSelection = criterionKey => {
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
            geolocation={geolocation}
            isSearchAroundMe={geolocationCriterion.isSearchAroundMe}
            location={location}
            match={match}
            query={query}
            redirectToSearchMainPage={redirectToSearchMainPage}
          />
        </Route>
        <Route path="/recherche-offres/criteres-localisation">
          <GeolocationCriteria
            activeCriterionLabel={geolocationCriterion.params.label}
            history={history}
            isGeolocationEnabled={isGeolocationEnabled}
            location={location}
            match={match}
            onCriterionSelection={this.handleGeolocationCriterionSelection}
          />
        </Route>
        <Route path="/recherche-offres/criteres-categorie">
          <CategoryCriteria
            activeCriterionLabel={categoryCriterion.label}
            history={history}
            location={location}
            match={match}
            onCriterionSelection={this.handleCategoryCriterionSelection}
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
