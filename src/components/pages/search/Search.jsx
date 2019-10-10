import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Fragment, PureComponent } from 'react'
import { Switch, Route } from 'react-router-dom'

import NavByOfferTypeContainer from './NavByOfferType/NavByOfferTypeContainer'
import NavResultsHeader from './NavResultsHeader'
import RecommendationDetailsContainer from './RecommendationDetails/RecommendationDetailsContainer'
import ResultsContainer from './Results/ResultsContainer'
import FilterControlsContainer from './FilterControls/FilterControlsContainer'
import {
  getDescriptionFromCategory,
  getVisibleParamsAreEmpty,
  INITIAL_FILTER_PARAMS,
  isInitialQueryWithoutFilters,
  translateBrowserUrlToApiUrl,
} from './helpers'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import { getRecommendationSearch } from './selectors/selectRecommendationsBySearchQuery'
import Icon from '../../layout/Icon/Icon'
import Spinner from '../../layout/Spinner/Spinner'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'

class Search extends PureComponent {
  constructor(props) {
    super(props)

    const { query } = props
    const queryParams = query.parse()

    this.state = {
      isLoading: false,
      isFilterVisible: false,
      keywordsKey: 0,
      keywordsValue: queryParams['mots-cles'],
    }
  }

  componentDidMount() {
    const { getTypes, query } = this.props

    getTypes()

    const queryParams = query.parse()
    if (queryParams.page) {
      query.change({ page: null })
    } else {
      this.handleRecommendationsRequest()
    }

    this.handleShouldRedirectToSearch()
    this.handleCategoryMissing()
  }

  componentDidUpdate(prevProps) {
    const { location, typeSublabelsAndDescription } = this.props
    if (location.search !== prevProps.location.search) {
      this.handleRecommendationsRequest()
      this.handleShouldRedirectToSearch()
    }

    if (typeSublabelsAndDescription !== prevProps.typeSublabelsAndDescription) {
      this.handleCategoryMissing()
    }
  }

  getBackToUrl = () => {
    const { match } = this.props
    const { params } = match
    const { details, results } = params
    if (details) {
      return null
    }
    if (results) {
      return '/recherche'
    }
  }

  getHeaderTitle = () => {
    const { match } = this.props
    const { params } = match
    const { results } = params
    let headerTitle = 'Recherche'
    if (results) {
      headerTitle = `${headerTitle} : résultats`
    }
    return headerTitle
  }

  handleCategoryMissing = () => {
    const { match, query, typeSublabelsAndDescription } = this.props
    const { categories } = query.parse()
    if (categories) return

    const { category, results } = match.params
    const isResultatsView = typeof results !== 'undefined'
    const shouldUpdateCategories = category && isResultatsView
    if (!shouldUpdateCategories) return

    const description = getDescriptionFromCategory(
      decodeURIComponent(category),
      typeSublabelsAndDescription
    )
    if (description) {
      query.change({ categories: category })
    }
  }

  handleRecommendationsRequest = () => {
    const { getRecommendations, location, query } = this.props
    const isResultatsView = location.pathname.includes('resultats')
    if (!isResultatsView) return
    const queryParams = query.parse()
    const apiParams = translateBrowserUrlToApiUrl(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/recommendations?${apiParamsString}`
    if (this.isFirstPageRequest(queryParams)) {
      this.setState({ isLoading: true })
    }
    const recommendationsAlreadyExist = this.isRecommendationFound()
    if (!recommendationsAlreadyExist) {
      getRecommendations(apiPath, this.handleDataSuccess)
    } else {
      this.setState({ isLoading: false })
    }
  }

  handleDataSuccess = () => {
    this.setState({ isLoading: false })
  }

  handleShouldRedirectToSearch = () => {
    const { history, query } = this.props
    const queryParams = query.parse()
    const queryParamsAreEmpty = getVisibleParamsAreEmpty(queryParams)
    const queryParamsAndKeywordsAreEmpty = queryParamsAreEmpty && !queryParams['mots-cles']
    if (queryParamsAndKeywordsAreEmpty) {
      history.replace('/recherche')
    }
  }

  reinitializeStates = () => {
    const { keywordsKey } = this.state

    this.setState({
      isLoading: false,
      isFilterVisible: false,
      // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
      // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
      // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
      // THE INPUT WITH A SYNCED DEFAULT VALUE
      keywordsKey: keywordsKey + 1,
      keywordsValue: '',
    })
  }

  handleOnSubmit = event => {
    const { match, query } = this.props
    const { params } = match
    const { category } = params
    const { value } = event.target.elements.keywords
    event.preventDefault()

    this.setState({ isFilterVisible: false })

    const nextPathname = `/recherche/resultats/${category || 'tout'}`
    query.change(
      {
        'mots-cles': value === '' ? null : value,
        page: 1,
      },
      { pathname: nextPathname }
    )
  }

  handleOnClickToggleFilterButton = isFilterVisible => () => {
    this.setState({ isFilterVisible: !isFilterVisible })
  }

  handleOnKeywordsChange = event => {
    this.setState({
      keywordsValue: event.target.value,
    })
  }

  handleOnKeywordsEraseClick = () => {
    const { keywordsKey } = this.state

    this.setState({
      // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
      // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
      // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
      // THE INPUT WITH A SYNCED DEFAULT VALUE
      keywordsKey: keywordsKey + 1,
      keywordsValue: '',
    })
  }

  isFirstPageRequest = queryParams => {
    const { page = '' } = queryParams
    return page === '1' || page === ''
  }

  isRecommendationFound = () => {
    const { location, recommendations, types } = this.props
    const searchQuery = getRecommendationSearch(location.search, types)
    const foundRecommendations = recommendations.filter(
      recommendation =>
        recommendation.search === searchQuery || `${recommendation.search}&page=1` === searchQuery
    )

    return foundRecommendations.length > 0 ? true : false
  }

  renderNavByOfferTypeContainer = typeSublabels => () => (
    <NavByOfferTypeContainer
      categories={typeSublabels}
      title="EXPLORER LES CATÉGORIES"
    />
  )

  renderSearchNavAndResults = () => {
    const {
      location,
      match,
      query,
      recommendations,
      typeSublabels,
      typeSublabelsAndDescription,
    } = this.props
    const { params } = match

    const queryParams = query.parse()
    const keywords = encodeURI(queryParams[`mots-cles`])
    let description
    const category = decodeURIComponent(queryParams.categories || params.category)
    if (location.pathname.includes('/resultats/')) {
      description = getDescriptionFromCategory(category, typeSublabelsAndDescription)
    }

    return (
      <Fragment>
        <NavResultsHeader
          category={category}
          description={description}
        />
        <ResultsContainer
          cameFromOfferTypesPage
          items={recommendations}
          keywords={keywords}
          typeSublabels={typeSublabels}
        />
      </Fragment>
    )
  }

  renderResults = () => {
    const { query, recommendations, typeSublabels } = this.props
    const queryParams = query.parse()
    const keywords =
      queryParams['mots-cles'] !== undefined ? encodeURI(queryParams['mots-cles']) : ''

    return (
      <ResultsContainer
        cameFromOfferTypesPage={false}
        items={recommendations}
        keywords={keywords}
        typeSublabels={typeSublabels}
      />
    )
  }

  renderControlsAndResults = () => {
    const { location, query, typeSublabels } = this.props
    const queryParams = query.parse()

    const { keywordsKey, keywordsValue, isFilterVisible, isLoading } = this.state

    const withoutFilters = isInitialQueryWithoutFilters(INITIAL_FILTER_PARAMS, queryParams)

    const iconFilterName = withoutFilters ? 'filter' : 'filter-active'

    const filtersToggleButtonClass = (isFilterVisible && 'filters-are-opened') || ''

    const isOneCharInKeywords = keywordsValue && keywordsValue.length > 0

    return (
      <Fragment>
        <div className="page-content">
          <form onSubmit={this.handleOnSubmit}>
            <div className="flex-columns items-start">
              <div
                className="field has-addons flex-columns flex-1"
                id="search-page-keywords-field"
              >
                <p
                  className="control has-icons-right flex-1"
                  key={keywordsKey}
                >
                  <label
                    className="is-hidden"
                    htmlFor="keywords"
                  >
                    {'Veuillez entrer un mot-clé'}
                  </label>
                  <input
                    className="input search-input"
                    defaultValue={keywordsValue}
                    id="keywords"
                    onChange={this.handleOnKeywordsChange}
                    placeholder="Saisir un mot-clé"
                    type="text"
                  />

                  {isOneCharInKeywords && (
                    <span className="icon flex-columns flex-center items-center is-right">
                      <button
                        className="no-background is-red-text"
                        id="refresh-keywords-button"
                        onClick={this.handleOnKeywordsEraseClick}
                        type="button"
                      >
                        <span
                          aria-hidden
                          className="icon-legacy-close"
                          title="Supprimer le mot-clé"
                        />
                      </button>
                    </span>
                  )}
                </p>
                <div className="control flex-0">
                  <button
                    disabled={!isOneCharInKeywords}
                    id="keywords-search-button"
                    type="submit"
                  >
                    {'Chercher'}
                  </button>
                </div>
              </div>
              <div
                className={`flex-0 text-center flex-rows flex-center pb12 ${filtersToggleButtonClass}`}
                id="search-filter-menu-toggle-button"
              >
                <button
                  className="no-background"
                  onClick={this.handleOnClickToggleFilterButton(isFilterVisible)}
                  type="button"
                >
                  <Icon svg={`ico-${isFilterVisible ? 'chevron-up' : iconFilterName}`} />
                </button>
              </div>
            </div>
            <FilterControlsContainer
              isVisible={isFilterVisible}
              onClickFilterButton={this.handleOnClickToggleFilterButton}
            />
          </form>
          <Switch location={location}>
            <Route
              exact
              path="/recherche/:menu(menu)?"
              render={this.renderNavByOfferTypeContainer(typeSublabels)}
            />
            {isLoading && <Spinner
              key="loader"
              label="Recherche en cours"
                          />}
            {!isLoading && (
              <Switch>
                <Route
                  path="/recherche/resultats/:category([A-Z][a-z]+)/:menu(menu)?"
                  render={this.renderSearchNavAndResults}
                  sensitive
                />
                <Route
                  path="/recherche/resultats/:menu(menu)?"
                  render={this.renderResults}
                />
              </Switch>
            )}
          </Switch>
        </div>
        <RelativeFooterContainer
          className="dotted-top-red"
          theme="white"
        />
      </Fragment>
    )
  }

  render() {
    return (
      <main className="search-page page with-footer with-header">
        <HeaderContainer
          backActionOnClick={this.reinitializeStates}
          backTo={this.getBackToUrl()}
          shouldBackFromDetails
          title={this.getHeaderTitle()}
        />
        {this.renderControlsAndResults()}
        <RecommendationDetailsContainer bookingPath="/recherche/resultats/:category?/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?" />
      </main>
    )
  }
}

Search.propTypes = {
  getRecommendations: PropTypes.func.isRequired,
  getTypes: PropTypes.func.isRequired,
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      category: PropTypes.string,
      details: PropTypes.string,
      results: PropTypes.string,
    }).isRequired,
  }).isRequired,
  query: PropTypes.shape().isRequired,
  recommendations: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  typeSublabels: PropTypes.arrayOf(PropTypes.string).isRequired,
  typeSublabelsAndDescription: PropTypes.arrayOf(
    PropTypes.shape({
      description: PropTypes.string,
      sublabel: PropTypes.string,
    })
  ).isRequired,
  types: PropTypes.arrayOf(
    PropTypes.shape({
      appLabel: PropTypes.string,
      description: PropTypes.string,
      id: PropTypes.number,
    })
  ).isRequired,
}

export default Search
