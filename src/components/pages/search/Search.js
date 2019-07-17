import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'
import { assignData, requestData } from 'redux-saga-data'

import Footer from './Footer'
import PageHeader from '../../layout/Header/PageHeader'
import NavByOfferTypeContainer from './searchByType/NavByOfferTypeContainer'
import NavResultsHeader from './NavResultsHeader'
import SearchFilterContainer from './searchFilters/SearchFilterContainer'
import SearchResultsContainer from './SearchResultsContainer'
import SearchDetailsContainer from './SearchDetailsContainer'
import {
  getDescriptionFromCategory,
  INITIAL_FILTER_PARAMS,
  isInitialQueryWithoutFilters,
  translateBrowserUrlToApiUrl,
} from './utils'
import Icon from '../../layout/Icon'

class Search extends PureComponent {
  constructor(props) {
    super(props)

    const { query } = props
    const queryParams = query.parse()

    this.state = {
      hasMore: false,
      isFilterVisible: false,
      keywordsKey: 0,
      keywordsValue: queryParams['mots-cles'],
    }

    props.dispatch(assignData({ searchRecommendations: [] }))
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

  clearSearchResults = value => {
    if (value === '') return
    const { dispatch } = this.props
    dispatch(assignData({ searchRecommendations: [] }))
  }

  handleCategoryMissing = () => {
    const { location, match, query, typeSublabelsAndDescription } = this.props
    const { categories } = query.parse()
    if (categories) return

    const { option } = match.params
    const isResultatsView = location.pathname.includes('/resultats/')
    const shouldUpdateCategories = option && isResultatsView
    if (!shouldUpdateCategories) return

    const description = getDescriptionFromCategory(
      decodeURIComponent(option),
      typeSublabelsAndDescription
    )
    if (description) {
      query.change({ categories: option })
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
    dispatch(
      requestData({
        apiPath,
        handleSuccess: (state, action) => {
          const { data } = action.payload
          const hasMore = data.length > 0
          this.setState({ hasMore })
        },
        stateKey: 'searchRecommendations',
      })
    )
  }

  goBack = () => {
    const { location, match } = this.props
    const {
      params: { option, subOption },
    } = match
    const isOfferVersoPage = option === 'item' || subOption === 'item'
    let url = '/recherche'

    if (isOfferVersoPage) {
      url = `${location.pathname.split('/item')[0]}${location.search}`
    }

    return url
  }

  reinitializeStates = () => {
    const { keywordsKey } = this.state

    this.setState({
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

  hasBackLink = location => (location.pathname.includes('/resultats') ? true : null)

  handleOnSubmit = event => {
    const { query } = this.props
    const { value } = event.target.elements.keywords
    event.preventDefault()

    this.setState({ isFilterVisible: false })

    this.clearSearchResults(value)

    query.change(
      {
        'mots-cles': value === '' ? null : value,
        page: null,
      },
      { pathname: '/recherche/resultats' }
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

  renderSearchDetailsContainer = route => <SearchDetailsContainer {...route} />

  renderNavByOfferTypeContainer = typeSublabels => () => (
    <NavByOfferTypeContainer
      categories={typeSublabels}
      title="EXPLORER LES CATÉGORIES"
    />
  )

  renderResults = () => {
    const {
      location,
      query,
      recommendations,
      typeSublabels,
      typeSublabelsAndDescription,
    } = this.props
    const queryParams = query.parse()
    const { hasMore } = this.state
    const keywords = queryParams[`mots-cles`]
    let description
    const category = decodeURIComponent(queryParams.categories)
    if (location.pathname.includes('/resultats/')) {
      description = getDescriptionFromCategory(category, typeSublabelsAndDescription)
    }

    return (
      <Fragment>
        <NavResultsHeader
          category={category}
          description={description}
        />
        <SearchResultsContainer
          cameFromOfferTypesPage
          hasMore={hasMore}
          items={recommendations}
          keywords={keywords}
          loadMoreHandler={this.loadMoreHandler}
          typeSublabels={typeSublabels}
        />
      </Fragment>
    )
  }

  renderSearchResultsContainer = () => {
    const { query, recommendations, typeSublabels } = this.props
    const { hasMore } = this.state
    const queryParams = query.parse()
    const keywords = queryParams[`mots-cles`]

    return (
      <SearchResultsContainer
        cameFromOfferTypesPage={false}
        hasMore={hasMore}
        items={recommendations}
        keywords={keywords}
        typeSublabels={typeSublabels}
      />
    )
  }

  renderSearchResult = () => {
    const { location, query, typeSublabels } = this.props
    const queryParams = query.parse()

    const { keywordsKey, keywordsValue, isFilterVisible } = this.state

    const whithoutFilters = isInitialQueryWithoutFilters(INITIAL_FILTER_PARAMS, queryParams)

    const iconFilterName = whithoutFilters ? 'filter' : 'filter-active'

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
            <SearchFilterContainer
              isVisible={isFilterVisible}
              key="SearchFilterContainer"
              onClickFilterButton={this.handleOnClickToggleFilterButton}
            />
          </form>
          <Switch location={location}>
            <Route
              exact
              path="/recherche/:menu(menu)?"
              render={this.renderNavByOfferTypeContainer(typeSublabels)}
            />
            <Route
              path="/recherche/resultats/:categorie([A-Z][a-z]+)/:menu(menu)?"
              render={this.renderResults}
              sensitive
            />
            <Route
              path="/recherche/resultats/:menu(menu)?"
              render={this.renderSearchResultsContainer}
            />
          </Switch>
        </div>
        <Footer />
      </Fragment>
    )
  }

  render() {
    const { location } = this.props

    let headerTitle = 'Recherche'
    if (location.pathname.includes('/resultats')) {
      headerTitle = `${headerTitle} : résultats`
    }

    return (
      <main
        className="search-page page with-footer with-header"
        role="main"
      >
        <PageHeader
          backActionOnClick={this.reinitializeStates}
          backTo={this.hasBackLink(location) && this.goBack()}
          title={headerTitle}
        />
        <Switch location={location}>
          <Route
            path="/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?"
            render={this.renderSearchDetailsContainer}
          />
          <Route
            path="/recherche/(resultats)?/:option?/:subOption(menu)?"
            render={this.renderSearchResult}
          />
        </Switch>
      </main>
    )
  }
}

Search.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  recommendations: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  typeSublabels: PropTypes.arrayOf(PropTypes.string).isRequired,
  typeSublabelsAndDescription: PropTypes.arrayOf(
    PropTypes.shape({
      description: PropTypes.string,
      sublabel: PropTypes.string,
    })
  ).isRequired,
}

export default Search
