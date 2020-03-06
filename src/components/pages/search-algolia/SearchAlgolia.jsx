import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { Criteria } from './Criteria/Criteria'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA } from './Criteria/criteriaEnums'
import { Home } from './Home/Home'
import SearchResults from './Result/SearchResults'

class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      geolocationCriterion: {
        isSearchAroundMe: props.isGeolocationEnabled,
        params: props.isGeolocationEnabled
          ? GEOLOCATION_CRITERIA.AROUND_ME
          : GEOLOCATION_CRITERIA.EVERYWHERE,
      },
      categoryCriterion: CATEGORY_CRITERIA.ALL,
    }
  }

  handleGeolocationCriterionSelection = criterionKey => () => {
    const { isUserAllowedToSelectCriterion, isGeolocationEnabled } = this.props
    if (!isUserAllowedToSelectCriterion(criterionKey, isGeolocationEnabled)) return

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
    const { match, query, redirectToSearchMainPage, history, geolocation } = this.props
    const { geolocationCriterion, categoryCriterion } = this.state

    return (
      <Switch>
        <Route
          exact
          path="/recherche-offres(/menu)?"
        >
          <Home
            categoryCriterion={categoryCriterion}
            geolocationCriterion={geolocationCriterion}
            history={history}
          />
        </Route>
        <Route path="/recherche-offres/resultats">
          <SearchResults
            categoriesFilter={categoryCriterion.filters}
            geolocation={geolocation}
            history={history}
            isSearchAroundMe={geolocationCriterion.isSearchAroundMe}
            match={match}
            query={query}
            redirectToSearchMainPage={redirectToSearchMainPage}
          />
        </Route>
        <Route path="/recherche-offres/criteres-localisation">
          <Criteria
            activeCriterionLabel={geolocationCriterion.params.label}
            criteria={GEOLOCATION_CRITERIA}
            history={history}
            match={match}
            onCriterionSelection={this.handleGeolocationCriterionSelection}
            title="Localisation"
          />
        </Route>
        <Route path="/recherche-offres/criteres-categorie">
          <Criteria
            activeCriterionLabel={categoryCriterion.label}
            criteria={CATEGORY_CRITERIA}
            history={history}
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
  history: PropTypes.shape({ push: PropTypes.func, location: PropTypes.shape() }).isRequired,
  isGeolocationEnabled: PropTypes.bool.isRequired,
  isUserAllowedToSelectCriterion: PropTypes.func.isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
}

export default SearchAlgolia
