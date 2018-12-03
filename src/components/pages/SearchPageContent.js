import { assignData, requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import { Icon } from '../layout/Icon'
import renderPageFooter from './search/Footer'
import renderPageHeader from './search/Header'
import NavByOfferType from './search/NavByOfferType'
import NavResultsHeader from './search/NavResultsHeader'
import SearchFilter from './search/SearchFilter'
import SearchResults from './search/SearchResults'
import isInitialQueryWithoutFilters, {
  getDescriptionForSublabel,
  INITIAL_FILTER_PARAMS,
  translateBrowserUrlToApiUrl,
} from './search/utils'

import Main from '../layout/Main'

class SearchPageContent extends PureComponent {
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
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props
    if (location.search !== prevProps.location.search) {
      this.handleRecommendationsRequest()
    }
  }

  handleRecommendationsRequest = () => {
    const { dispatch, match, query } = this.props

    if (match.params.view !== 'resultats') {
      return
    }

    const queryParams = query.parse()
    const apiParams = translateBrowserUrlToApiUrl(queryParams)
    const apiParamsString = stringify(apiParams)
    const path = `recommendations?${apiParamsString}`
    dispatch(
      requestData('GET', path, {
        handleSuccess: (state, action) => {
          if (action.data && action.data.length === 0) {
            this.setState({ hasMore: false })
          } else {
            this.setState({ hasMore: true })
          }
        },
      })
    )
  }

  onBackToSearchHome = () => {
    const { keywordsKey } = this.state
    const { query } = this.props

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
        jours: null,
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
      location,
      match,
      query,
      recommendations,
      typeSublabels,
      typeSublabelsAndDescription,
    } = this.props
    const queryParams = query.parse()

    const { hasMore, keywordsKey, keywordsValue, isFilterVisible } = this.state
    const onResultPage = match.params.view === 'resultats'
    const keywords = queryParams[`mots-cles`]

    const backButton = onResultPage && {
      onClick: () => this.onBackToSearchHome(),
    }

    const whithoutFilters = isInitialQueryWithoutFilters(
      INITIAL_FILTER_PARAMS,
      queryParams
    )

    const iconName = whithoutFilters ? 'filter' : 'filter-active'

    const filtersToggleButtonClass =
      (isFilterVisible && 'filters-are-opened') || ''

    const isOneCharInKeywords = keywordsValue && keywordsValue.length > 0

    // ******************** Displaying datas helpers ********************** //
    const searchPageTitle = onResultPage ? 'Recherche : résultats' : 'Recherche'

    let description
    const category = decodeURIComponent(queryParams.categories)
    if (location.pathname.indexOf('/resultats/') !== -1) {
      description = getDescriptionForSublabel(
        category,
        typeSublabelsAndDescription
      )
    }

    return (
      <Main
        id="search-page"
        backButton={backButton}
        closeSearchButton
        footer={renderPageFooter}
        handleDataRequest={() => {}}
        header={renderPageHeader}
        name="search"
        pageTitle={searchPageTitle}
      >
        <form onSubmit={this.onSubmit}>
          <div className="flex-columns items-start">
            <div
              id="search-page-keywords-field"
              className="field has-addons flex-columns flex-1"
            >
              <p className="control has-icons-right flex-1" key={keywordsKey}>
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
                onClick={this.onClickOpenCloseFilterDiv(isFilterVisible)}
              >
                <Icon
                  svg={`ico-${isFilterVisible ? 'chevron-up' : iconName}`}
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
            path="/recherche"
            render={() => (
              <NavByOfferType
                title="PAR CATÉGORIES"
                typeSublabels={typeSublabels}
              />
            )}
          />
          <Route
            path="/recherche/resultats/:categorie"
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
            path="/recherche/resultats"
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
      </Main>
    )
  }
}

SearchPageContent.propTypes = {
  dispatch: PropTypes.func.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  query: PropTypes.object.isRequired,
  recommendations: PropTypes.array.isRequired,
  typeSublabels: PropTypes.array.isRequired,
  typeSublabelsAndDescription: PropTypes.array.isRequired,
}

export default SearchPageContent
