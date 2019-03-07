import { assignData, requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import BackButton from '../../layout/BackButton'
import { Icon } from '../../layout/Icon'
import Footer from './Footer'
import Header from './Header'
import NavByOfferType from './NavByOfferType'
import NavResultsHeader from './NavResultsHeader'
import SearchFilter from './SearchFilter'
import SearchResults from './SearchResults'
import SearchDetails from './SearchDetails'
import isInitialQueryWithoutFilters, {
  getDescriptionForSublabel,
  INITIAL_FILTER_PARAMS,
  translateBrowserUrlToApiUrl,
} from './utils'

class RawSearch extends PureComponent {
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

    props.dispatch(assignData({ recommendations: [] }))
  }

  componentDidMount() {
    const { dispatch, query } = this.props

    dispatch(requestData('GET', 'types'))

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

  handleCategoryMissing = () => {
    const { location, match, query, typeSublabelsAndDescription } = this.props
    const {
      params: { option },
    } = match
    const { categories } = query.parse()

    if (categories) {
      return
    }

    if (option && location.pathname.includes('/resultats/')) {
      const description = getDescriptionForSublabel(
        decodeURIComponent(option),
        typeSublabelsAndDescription
      )
      if (description) {
        query.change({ categories: option })
      }
    }
  }

  handleRecommendationsRequest = () => {
    const { dispatch, location, query } = this.props

    if (!location.pathname.includes('resultats')) {
      return
    }

    const queryParams = query.parse()
    const apiParams = translateBrowserUrlToApiUrl(queryParams)
    const apiParamsString = stringify(apiParams)
    const path = `recommendations?${apiParamsString}`
    dispatch(
      requestData('GET', path, {
        handleSuccess: (state, action) => {
          const hasMore = action.data && action.data.length > 0
          this.setState({ hasMore })
        },
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
    const { dispatch, query } = this.props
    const { value } = event.target.elements.keywords
    event.preventDefault()

    this.setState({ isFilterVisible: false })

    if (value !== '') {
      dispatch(assignData({ recommendations: [] }))
    }

    query.change(
      {
        'mots-cles': value === '' ? null : value,
        page: null,
      },
      { pathname: '/recherche/resultats' }
    )
  }

  onClickOpenCloseFilterDiv = isFilterVisible => () => {
    this.setState({ isFilterVisible: !isFilterVisible })
  }

  onKeywordsChange = event => {
    this.setState({
      keywordsValue: event.target.value,
    })
  }

  onKeywordsEraseClick = () => {
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

    const iconName = whithoutFilters ? 'filter' : 'filter-active'

    const filtersToggleButtonClass =
      (isFilterVisible && 'filters-are-opened') || ''

    const isOneCharInKeywords = keywordsValue && keywordsValue.length > 0

    // ******************** Displaying datas helpers ********************** //
    let headerTitle = 'Recherche'
    if (location.pathname.includes('/resultats'))
      headerTitle = `${headerTitle} : résultats`

    let description
    const category = decodeURIComponent(queryParams.categories)
    if (location.pathname.includes('/resultats/')) {
      description = getDescriptionForSublabel(
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
            title="Retour sur la page découverte"
          />
        </button>
        <Switch location={location}>
          <Route
            path="/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?"
            render={route => <SearchDetails {...route} />}
          />
          <Route
            path="/recherche/(resultats)?/:option?/:subOption(menu)?"
            render={() => (
              <Fragment>
                <div className="page-content is-relative">
                  <form onSubmit={this.onSubmit}>
                    <div className="flex-columns items-start">
                      <div
                        id="search-page-keywords-field"
                        className="field has-addons flex-columns flex-1"
                      >
                        <p
                          className="control has-icons-right flex-1"
                          key={keywordsKey}
                        >
                          <input
                            // FIXME autoFocus Github Issue #867
                            id="keywords"
                            defaultValue={keywordsValue}
                            className="input search-input"
                            placeholder="Un mot-clé"
                            type="text"
                            onChange={this.onKeywordsChange}
                          />
                          {isOneCharInKeywords && (
                            <span className="icon is-small is-right">
                              <button
                                className="no-border no-background is-red-text"
                                id="refresh-keywords-button"
                                onClick={this.onKeywordsEraseClick}
                                type="button"
                              >
                                <span
                                  aria-hidden
                                  className="icon-legacy-close"
                                  title=""
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
                            Chercher
                          </button>
                        </div>
                      </div>
                      {/* ************************* BOUTON OPEN CLOSE FILTER ************************* */}
                      <div
                        id="search-filter-menu-toggle-button"
                        className={`flex-0 text-center flex-rows flex-center pb12 ${filtersToggleButtonClass}`}
                      >
                        <button
                          type="button"
                          className="no-border no-background no-outline "
                          onClick={this.onClickOpenCloseFilterDiv(
                            isFilterVisible
                          )}
                        >
                          <Icon
                            svg={`ico-${
                              isFilterVisible ? 'chevron-up' : iconName
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                  </form>

                  <SearchFilter
                    isVisible={isFilterVisible}
                    onKeywordsEraseClick={this.onKeywordsEraseClick}
                  />

                  <Switch location={location}>
                    <Route
                      exact
                      path="/recherche/:menu(menu)?"
                      render={() => (
                        <NavByOfferType
                          title="PAR CATÉGORIES"
                          typeSublabels={typeSublabels}
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
                          <SearchResults
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
                        <SearchResults
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

RawSearch.propTypes = {
  dispatch: PropTypes.func.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  query: PropTypes.object.isRequired,
  recommendations: PropTypes.array.isRequired,
  typeSublabels: PropTypes.array.isRequired,
  typeSublabelsAndDescription: PropTypes.array.isRequired,
}

export default RawSearch
