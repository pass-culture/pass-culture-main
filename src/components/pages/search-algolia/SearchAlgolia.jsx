import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import GeolocationCriteria from './Criteria/GeolocationCriteria'
import { GEOLOCATION_CRITERIA } from './Criteria/geolocationCriteriaValues'
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
    const { geolocationCriterion } = this.state

    return (
      <Switch>
        <Route
          exact
          path="/recherche-offres(/menu)?"
        >
          <SearchHome
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
            activeGeolocationLabel={geolocationCriterion.params.label}
            history={history}
            isGeolocationEnabled={isGeolocationEnabled}
            location={location}
            match={match}
            onGeolocationCriterionSelection={this.handleGeolocationCriterionSelection}
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
