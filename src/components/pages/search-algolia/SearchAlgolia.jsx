import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { CATEGORY_CRITERIA, GEOLOCATION_CRITERIA, SORT_CRITERIA } from './Criteria/criteriaEnums'
import { Home } from './Home/Home'
import SearchResults from './Result/SearchResults'
import CriteriaLocation from './CriteriaLocation/CriteriaLocation'
import CriteriaCategory from './CriteriaCategory/CriteriaCategory'
import CriteriaSort from './CriteriaSort/CriteriaSort'

const DEFAULT_META_VIEWPORT_CONTENT =
  'width=device-width, initial-scale=1, user-scalable=no, shrink-to-fit=no'

class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      categoryCriterion: CATEGORY_CRITERIA.ALL,
      geolocationCriterion: {
        isSearchAroundMe: false,
        params: GEOLOCATION_CRITERIA.EVERYWHERE,
      },
      sortCriterion: SORT_CRITERIA.RELEVANCE,
    }
  }

  componentDidMount() {
    this.preventWindowResize()
  }

  componentWillUnmount() {
    this.resetWindowResize()
  }

  preventWindowResize() {
    const pageDefaultHeight = document.querySelector('body').offsetHeight
    window.onresize = () => {
      document
        .querySelector('meta[name=viewport]')
        .setAttribute('content', `height=${pageDefaultHeight}px, ${DEFAULT_META_VIEWPORT_CONTENT}`)
    }
  }

  resetWindowResize() {
    document
      .querySelector('meta[name=viewport]')
      .setAttribute('content', DEFAULT_META_VIEWPORT_CONTENT)
    window.onresize = null
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

  handleCategoryCriterionSelection = criterionKey => () => {
    this.setState({
      categoryCriterion: CATEGORY_CRITERIA[criterionKey],
    })
    const { redirectToSearchMainPage } = this.props
    redirectToSearchMainPage()
  }

  handleSortCriterionSelection = criterionKey => {
    this.setState({
      sortCriterion: SORT_CRITERIA[criterionKey],
    })
    const { redirectToSearchMainPage } = this.props
    redirectToSearchMainPage()
  }

  render() {
    const { match, query, redirectToSearchMainPage, history, geolocation } = this.props
    const { categoryCriterion, geolocationCriterion, sortCriterion } = this.state

    return (
      <Switch>
        <Route
          exact
          path="/recherche(/menu)?"
        >
          <Home
            categoryCriterion={categoryCriterion}
            geolocationCriterion={geolocationCriterion}
            history={history}
            sortCriterion={sortCriterion}
          />
        </Route>
        <Route path="/recherche/resultats">
          <SearchResults
            criteria={{
              categories: categoryCriterion.facetFilter ? [categoryCriterion.facetFilter] : [],
              isSearchAroundMe: geolocationCriterion.isSearchAroundMe,
              sortBy: sortCriterion.index,
            }}
            geolocation={geolocation}
            history={history}
            match={match}
            query={query}
            redirectToSearchMainPage={redirectToSearchMainPage}
            search={history.location.search}
          />
        </Route>
        <Route path="/recherche/criteres-localisation">
          <CriteriaLocation
            activeCriterionLabel={geolocationCriterion.params.label}
            backTo="/recherche"
            criteria={GEOLOCATION_CRITERIA}
            geolocation={geolocation}
            history={history}
            match={match}
            onCriterionSelection={this.handleGeolocationCriterionSelection}
            title="Localisation"
          />
        </Route>
        <Route path="/recherche/criteres-categorie">
          <CriteriaCategory
            activeCriterionLabel={categoryCriterion.label}
            backTo="/recherche"
            criteria={CATEGORY_CRITERIA}
            history={history}
            match={match}
            onCriterionSelection={this.handleCategoryCriterionSelection}
            title="Catégories"
          />
        </Route>
        <Route path="/recherche/criteres-tri">
          <CriteriaSort
            activeCriterionLabel={sortCriterion.label}
            backTo="/recherche"
            criteria={SORT_CRITERIA}
            geolocation={geolocation}
            history={history}
            match={match}
            onCriterionSelection={this.handleSortCriterionSelection}
            title="Trier par"
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
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
}

export default SearchAlgolia
