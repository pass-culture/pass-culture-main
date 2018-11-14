import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import { Icon, requestData } from 'pass-culture-shared'

import renderPageFooter from './search/Footer'
import renderPageHeader from './search/Header'
import NavByOfferType from './search/NavByOfferType'
import NavResultsHeader from './search/NavResultsHeader'
import SearchFilter from './search/SearchFilter'
import SearchResults from './search/SearchResults'
import filterIconByState, {
  getDescriptionForSublabel,
  INITIAL_FILTER_PARAMS,
  isSearchFiltersAdded,
} from './search/utils'
import Main from '../layout/Main'

class SearchPageContent extends PureComponent {
  constructor(props) {
    super(props)
    console.log('>>>>> IN CONSTRUCTOR Pagination', props.pagination.windowQuery)
    console.log('>>>>> IN CONSTRUCTOR match', props.match.params)
    this.state = {
      keywordsKey: 0,
      keywordsValue: get(props, `pagination.windowQuery.mots-cles`),
      withFilter: false,
    }
  }

  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { dispatch, location, match, pagination, search } = this.props
    // pagination props comes from the hoc withPagination from pass-culture-shared folder
    const { apiQueryString, goToNextPage, page } = pagination
    const { withFilter } = this.state

    // BECAUSE THE INFINITE SCROLLER CALLS ONCE THIS FUNCTION
    // BUT THEN PUSH THE SEARCH TO PAGE + 1
    // WE PASS AGAIN HERE FOR THE SAME PAGE
    // SO WE NEED TO PREVENT A SECOND CALL
    if (page !== 1 && search.page && page === Number(search.page)) {
      return
    }

    dispatch(requestData('GET', 'types'))

    const len = get(location, 'search.length')
    if (!len) return

    const path = `recommendations?page=${page}&${apiQueryString}`

    dispatch(
      requestData('GET', path, {
        handleFail,
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          if (match.params.view === 'resultats' && !withFilter) {
            goToNextPage()
          }
        },
      })
    )
  }

  loadMoreHandler = (handleSuccess, handleFail) => {
    this.handleDataRequest(handleSuccess, handleFail)
    const { history, location, pagination } = this.props
    const { windowQueryString, page } = pagination
    history.push(`${location.pathname}?page=${page}&${windowQueryString}`)
  }

  onBackToSearchHome = (pathname, pagination, keywordsKey) => {
    this.setState({
      // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
      // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
      // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
      // THE INPUT WITH A SYNCED DEFAULT VALUE
      keywordsKey: keywordsKey + 1,
      keywordsValue: '',
      withFilter: false,
    })
    pagination.change(
      {
        categories: null,
        date: null,
        jours: null,
        'mots-cles': null,
      },
      {
        pathname,
      }
    )
  }

  onSubmit = event => {
    const { pagination } = this.props
    const { value } = event.target.elements.keywords

    event.preventDefault()

    this.setState({ withFilter: false })

    pagination.change(
      {
        'mots-cles': value === '' ? null : value,
      },
      {
        isClearingData: value !== '',
        pathname: '/recherche/resultats',
      }
    )
  }

  onClickOpenCloseFilterDiv = withFilter => () => {
    this.setState({ withFilter: !withFilter })
  }
  // onClick={() => this.setState(prev => ({ withFilter: !prev.withFilter }))}

  onKeywordsChange = event => {
    this.setState({
      keywordsValue: event.target.value,
    })
  }

  onKeywordsEraseClick = (pathname, pagination, keywordsKey) => () => {
    this.setState({
      // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
      // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
      // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
      // THE INPUT WITH A SYNCED DEFAULT VALUE
      keywordsKey: keywordsKey + 1,
      keywordsValue: '',
    })
    pagination.change(
      {
        'mots-cles': null,
      },
      {
        pathname,
      }
    )
  }

  render() {
    const {
      location,
      match,
      pagination,
      recommendations,
      typeSublabels,
      typeSublabelsAndDescription,
    } = this.props

    console.log('>>>>> IN CONSTRUCTOR Pagination', pagination.windowQuery)
    console.log('>>>>> IN CONSTRUCTOR match', match.params)
    console.log('>>>>> IN CONSTRUCTOR location', location)

    const { keywordsKey, keywordsValue, withFilter } = this.state

    const { windowQuery } = pagination

    // ************************* HELPERS ****************************
    // FIX ME
    // match: {
    //   params: {
    //     categorie: undefined,
    //     view: undefined
    //   }
    // },
    // Cannot read property 'mots-cles' of undefined
    const onResultPage = match.params.view === 'resultats'
    const keywords = get(windowQuery, `mots-cles`)

    const backButton = onResultPage && {
      onClick: () =>
        this.onBackToSearchHome('/recherche', pagination, keywordsKey),
    }

    const filtersActive = isSearchFiltersAdded(
      INITIAL_FILTER_PARAMS,
      windowQuery
    )

    const isfilterIconActive = filterIconByState(filtersActive)
    const filtersToggleButtonClass = (withFilter && 'filters-are-opened') || ''

    const isOneCharInKeywords = get(keywordsValue, 'length') > 0

    // ************************* DATAS **************************** //
    const searchPageTitle = onResultPage ? 'Recherche : résultats' : 'Recherche'

    let description
    const category = decodeURIComponent(pagination.windowQuery.categories)
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
        handleDataRequest={this.handleDataRequest}
        header={renderPageHeader}
        pageTitle={searchPageTitle}
        name="search"
        footer={renderPageFooter}
        closeSearchButton
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
                      type="button"
                      className="no-border no-background is-red-text"
                      id="refresh-keywords-button"
                      onClick={this.onKeywordsEraseClick(
                        '/recherche/resultats',
                        pagination,
                        keywordsKey
                      )}
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
                onClick={this.onClickOpenCloseFilterDiv(withFilter)}
              >
                <Icon
                  svg={`ico-${withFilter ? 'chevron-up' : isfilterIconActive}`}
                />
              </button>
            </div>
          </div>
        </form>

        <SearchFilter isVisible={withFilter} pagination={pagination} />

        <Switch location={location}>
          <Route
            exact
            path="/recherche"
            render={() => (
              <NavByOfferType
                pagination={pagination}
                title="PAR CATÉGORIES"
                typeSublabels={typeSublabels}
              />
            )}
          />
          <Route
            path="/recherche/resultats/:categorie"
            render={() => [
              <NavResultsHeader
                category={category}
                description={description}
              />,
              <SearchResults
                keywords={keywords}
                items={recommendations}
                loadMoreHandler={this.loadMoreHandler}
                pagination={pagination}
                typeSublabels={typeSublabels}
                withNavigation
              />,
            ]}
          />
          <Route
            path="/recherche/resultats"
            render={() => (
              <SearchResults
                keywords={keywords}
                items={recommendations}
                loadMoreHandler={this.loadMoreHandler}
                pagination={pagination}
                typeSublabels={typeSublabels}
                withNavigation={false}
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
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  pagination: PropTypes.object.isRequired,
  recommendations: PropTypes.array.isRequired,
  search: PropTypes.object.isRequired,
  typeSublabels: PropTypes.array.isRequired,
  typeSublabelsAndDescription: PropTypes.array.isRequired,
}

export default SearchPageContent
