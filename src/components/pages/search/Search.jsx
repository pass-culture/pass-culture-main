import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Fragment, PureComponent } from 'react'
import { Switch, Route } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import NavByOfferTypeContainer from './NavByOfferType/NavByOfferTypeContainer'
import NavResultsHeader from './NavResultsHeader'
import RecommendationDetailsContainer from './RecommendationDetails/RecommendationDetailsContainer'
import ResultsContainer from './Results/ResultsContainer'
import FilterControlsContainer from './FilterControls/FilterControlsContainer'
import {
  getDescriptionFromCategory,
  INITIAL_FILTER_PARAMS,
  isInitialQueryWithoutFilters,
  translateBrowserUrlToApiUrl,
} from './helpers'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import Icon from '../../layout/Icon'
import Spinner from '../../layout/Spinner'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import { recommendationNormalizer } from '../../../utils/normalizers'

class Search extends PureComponent {
  constructor(props) {
    super(props)

    const { query } = props
    const queryParams = query.parse()

    this.state = {
      isLoading: false,
      hasMore: false,
      isFilterVisible: false,
      keywordsKey: 0,
      keywordsValue: queryParams['mots-cles'],
    }
  }

  componentDidMount() {
    const { dispatch, query } = this.props

    dispatch(requestData({ apiPath: '/types' }))

    const queryParams = query.parse()
    if (queryParams.page) {
      query.change({ page: null })
    } else {
      this.handleRecommendationsRequest()
    }

    this.handleCategoryMissing()
  }

  componentDidUpdate(prevProps) {
    const { location, typeSublabelsAndDescription } = this.props
    if (location.search !== prevProps.location.search) {
      this.handleRecommendationsRequest()
    }

    if (typeSublabelsAndDescription !== prevProps.typeSublabelsAndDescription) {
      this.handleCategoryMissing()
    }
  }

  componentWillUnmount() {
    const { resetPageData } = this.props
    resetPageData()
  }

  clearSearchResults = value => {
    const { resetPageData } = this.props
    if (value === '') return
    resetPageData()
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
    const { dispatch, location, query } = this.props
    const isResultatsView = location.pathname.includes('resultats')
    if (!isResultatsView) return

    const queryParams = query.parse()
    const apiParams = translateBrowserUrlToApiUrl(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/recommendations?${apiParamsString}`
    if (this.isFirstPageRequest(queryParams)) {
      this.setState({ isLoading: true })
    }
    dispatch(
      requestData({
        apiPath,
        handleSuccess: (state, action) => {
          const { data } = action.payload
          const hasMore = data.length > 0
          this.setState({ hasMore, isLoading: false })
        },
        normalizer: recommendationNormalizer,
      })
    )
  }

  reinitializeStates = () => {
    const { keywordsKey } = this.state

    this.setState({
      isLoading: false,
      hasMore: false,
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
    const { query } = this.props
    const { value } = event.target.elements.keywords
    event.preventDefault()

    this.setState({ isFilterVisible: false })

    this.clearSearchResults(value)

    query.change(
      {
        'mots-cles': value === '' ? null : value,
        page: 1,
      },
      { pathname: '/recherche/resultats/tout' }
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
    const { history } = this.props

    this.setState(
      {
        // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
        // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
        // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
        // THE INPUT WITH A SYNCED DEFAULT VALUE
        keywordsKey: keywordsKey + 1,
        keywordsValue: '',
      },
      () => history.push('/recherche/resultats')
    )
  }

  isFirstPageRequest = queryParams => {
    const { page = '' } = queryParams
    return page === ''
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
    const { hasMore } = this.state

    const queryParams = query.parse()
    const keywords = queryParams[`mots-cles`]
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
          hasMore={hasMore}
          items={recommendations}
          keywords={keywords}
          typeSublabels={typeSublabels}
        />
      </Fragment>
    )
  }

  renderResults = () => {
    const { query, recommendations, typeSublabels } = this.props
    const { hasMore } = this.state
    const queryParams = query.parse()
    const keywords = queryParams[`mots-cles`]

    return (
      <ResultsContainer
        cameFromOfferTypesPage={false}
        hasMore={hasMore}
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
                    placeholder="Un mot-clé"
                    type="text"
                  />

                  {isOneCharInKeywords && (
                    <span className="icon flex-columns flex-center items-center is-right">
                      <button
                        className="no-border no-background is-red-text"
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
                    className="button is-rounded is-medium"
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
                  className="no-border no-background no-outline"
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
      <main
        className="search-page page with-footer with-header"
        role="main"
      >
        <HeaderContainer
          backActionOnClick={this.reinitializeStates}
          backTo={this.getBackToUrl()}
          shouldBackFromDetails
          title={this.getHeaderTitle()}
        />
        {this.renderControlsAndResults()}
        <RecommendationDetailsContainer bookingPath="/recherche/resultats/:category?/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:bookings(reservations)/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?" />
      </main>
    )
  }
}

Search.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
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
  resetPageData: PropTypes.func.isRequired,
  typeSublabels: PropTypes.arrayOf(PropTypes.string).isRequired,
  typeSublabelsAndDescription: PropTypes.arrayOf(
    PropTypes.shape({
      description: PropTypes.string,
      sublabel: PropTypes.string,
    })
  ).isRequired,
}

export default Search
