import { assignData } from 'fetch-normalize-data'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import Footer from './Footer'
import Header from './Header'
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
import BackButton from '../../layout/BackButton'
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

  onBackToSearchHome = () => {
    const { keywordsKey } = this.state
    const { history, location, match, query } = this.props
    const {
      params: { option, subOption },
    } = match
    const isItemPage = option === 'item' || subOption === 'item'

    if (isItemPage) {
      const nextUrl = `${location.pathname.split('/item')[0]}${location.search}`
      history.push(nextUrl)
      return
    }

    this.setState({
      // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
      // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
      // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
      // THE INPUT WITH A SYNCED DEFAULT VALUE
      isFilterVisible: false,
      keywordsKey: keywordsKey + 1,
      keywordsValue: '',
    })
    query.change(
      {
        categories: null,
        date: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        'mots-cles': null,
        page: null,
      },
      {
        pathname: '/recherche',
      }
    )
  }

  onSubmit = event => {
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

  onClickToggleFilterButton = isFilterVisible => {
    this.setState({ isFilterVisible: !isFilterVisible })
  }

  onKeywordsChange = event => {
    this.setState({
      keywordsValue: event.target.value,
    })
  }

  onKeywordsEraseClick = () => {
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

  render() {
    const {
      history,
      location,
      query,
      recommendations,
      typeSublabels,
      typeSublabelsAndDescription,
    } = this.props
    const queryParams = query.parse()

    const { hasMore, keywordsKey, keywordsValue, isFilterVisible } = this.state
    const keywords = queryParams[`mots-cles`]

    const whithoutFilters = isInitialQueryWithoutFilters(
      INITIAL_FILTER_PARAMS,
      queryParams
    )

    const iconFilterName = whithoutFilters ? 'filter' : 'filter-active'

    const filtersToggleButtonClass =
      (isFilterVisible && 'filters-are-opened') || ''

    const isOneCharInKeywords = keywordsValue && keywordsValue.length > 0

    let headerTitle = 'Recherche'
    if (location.pathname.includes('/resultats')) {
      headerTitle = `${headerTitle} : résultats`
    }

    let description
    const category = decodeURIComponent(queryParams.categories)
    if (location.pathname.includes('/resultats/')) {
      description = getDescriptionFromCategory(
        category,
        typeSublabelsAndDescription
      )
    }

    return (
      <main role="main" className="search-page page with-footer with-header">
        <Header title={headerTitle} />
        {location.pathname.includes('/resultats') && (
          <BackButton onClick={this.onBackToSearchHome} />
        )}
        <button
          type="button"
          id="search-close-button"
          className="pc-text-button is-absolute fs16"
          onClick={() => history.push('/decouverte')}
        >
          <span
            aria-hidden
            className="icon-legacy-close is-white-text"
            title="Retourner à la page découverte"
          />
        </button>
        <Switch location={location}>
          <Route
            path="/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?"
            render={route => <SearchDetailsContainer {...route} />}
          />
          <Route
            path="/recherche/(resultats)?/:option?/:subOption(menu)?"
            render={() => (
              <Fragment>
                <div className="page-content">
                  <form onSubmit={this.onSubmit}>
                    <div className="flex-columns items-start">
                      <div
                        className="field has-addons flex-columns flex-1"
                        id="search-page-keywords-field"
                      >
                        <p
                          className="control has-icons-right flex-1"
                          key={keywordsKey}
                        >
                          <label className="is-hidden" htmlFor="keywords">
                            Veuillez entrer un mot-clé
                          </label>
                          <input
                            className="input search-input"
                            defaultValue={keywordsValue}
                            id="keywords"
                            onChange={this.onKeywordsChange}
                            placeholder="Un mot-clé"
                            type="text"
                          />

                          {isOneCharInKeywords && (
                            <span className="icon flex-columns flex-center items-center is-right">
                              <button
                                className="no-border no-background is-red-text"
                                id="refresh-keywords-button"
                                onClick={this.onKeywordsEraseClick}
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
                            id="keywords-search-button"
                            type="submit"
                            disabled={!isOneCharInKeywords}
                          >
                            {'Chercher'}
                          </button>
                        </div>
                      </div>
                      <div
                        id="search-filter-menu-toggle-button"
                        className={`flex-0 text-center flex-rows flex-center pb12 ${filtersToggleButtonClass}`}
                      >
                        <button
                          type="button"
                          className="no-border no-background no-outline"
                          onClick={() =>
                            this.onClickToggleFilterButton(isFilterVisible)
                          }
                        >
                          <Icon
                            svg={`ico-${
                              isFilterVisible ? 'chevron-up' : iconFilterName
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                    <SearchFilterContainer
                      key="SearchFilterContainer"
                      isVisible={isFilterVisible}
                      onClickFilterButton={this.onClickToggleFilterButton}
                    />
                  </form>
                  <Switch location={location}>
                    <Route
                      exact
                      path="/recherche/:menu(menu)?"
                      render={() => (
                        <NavByOfferTypeContainer
                          title="EXPLORER LES CATÉGORIES"
                          categories={typeSublabels}
                        />
                      )}
                    />
                    <Route
                      path="/recherche/resultats/:categorie([A-Z][a-z]+)/:menu(menu)?"
                      sensitive
                      render={() => (
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
                      )}
                    />
                    <Route
                      path="/recherche/resultats/:menu(menu)?"
                      render={() => (
                        <SearchResultsContainer
                          cameFromOfferTypesPage={false}
                          hasMore={hasMore}
                          items={recommendations}
                          keywords={keywords}
                          typeSublabels={typeSublabels}
                        />
                      )}
                    />
                  </Switch>
                </div>
                <Footer />
              </Fragment>
            )}
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
  recommendations: PropTypes.array.isRequired,
  typeSublabels: PropTypes.array.isRequired,
  typeSublabelsAndDescription: PropTypes.array.isRequired,
}

export default Search
