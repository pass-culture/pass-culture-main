import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import { compose } from 'redux'

import {
  Icon,
  requestData,
  withLogin,
  withPagination,
} from 'pass-culture-shared'

import NavByOfferType from './search/NavByOfferType'
import SearchFilter from './search/SearchFilter'
import SearchResults from './search/SearchResults'
import filterIconByState, {
  INITIAL_FILTER_PARAMS,
  isSearchFiltersAdded,
} from './search/utils'
import Main from '../layout/Main'
import NavigationFooter from '../layout/NavigationFooter'
import { selectRecommendations } from '../../selectors'
import { mapApiToWindow, windowToApiQuery } from '../../utils/pagination'

const renderPageHeader = () => (
  <header>
    <h1>
Recherche
    </h1>
  </header>
)

const renderPageFooter = () => (
  <NavigationFooter theme="white" className="dotted-top-red" />
)

class SearchPage extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      keywordsKey: 0,
      keywordsValue: get(
        props,
        `pagination.windowQuery.${mapApiToWindow.search}`
      ),
      withFilter: false,
    }
  }

  onSubmit = event => {
    const { pagination } = this.props
    const { value } = event.target.elements.search

    event.preventDefault()

    pagination.change(
      {
        [mapApiToWindow.search]: value === '' ? null : value,
      },
      { pathname: '/recherche/resultats' }
    )
  }

  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { dispatch, location, match, pagination, search } = this.props
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

  render() {
    const { history, location, match, pagination, recommendations } = this.props
    const { windowQuery } = pagination
    const { keywordsKey, keywordsValue, withFilter } = this.state

    const keywords = windowQuery[mapApiToWindow.search]

    const filtersActive = isSearchFiltersAdded(
      INITIAL_FILTER_PARAMS,
      windowQuery
    )
    const isfilterIconActive = filterIconByState(filtersActive)

    return (
      <Main
        backButton={
          match.params.view === 'resultats' && {
            onClick: () => history.push('/recherche'),
          }
        }
        handleDataRequest={this.handleDataRequest}
        header={renderPageHeader}
        name="search"
        footer={renderPageFooter}
      >
        <form className="section" onSubmit={this.onSubmit}>
          <div className="field has-addons">
            <p
              className="control has-icons-right is-expanded"
              key={keywordsKey}
            >
              <input
                id="search"
                defaultValue={keywordsValue}
                className="input search-input"
                placeholder="Saisissez une recherche"
                type="text"
                onChange={e => this.setState({ keywordsValue: e.target.value })}
              />

              {get(keywordsValue, 'length') > 0 && (
                <span className="icon is-small is-right">
                  <button
                    type="button"
                    className="no-border no-background is-red-text"
                    id="refresh-keywords-button"
                    onClick={() =>
                      this.setState({
                        // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
                        // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
                        // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
                        // THE INPUT WITH A SYNCED DEFAULT VALUE
                        keywordsKey: keywordsKey + 1,
                        keywordsValue: '',
                      })
                    }
                  >
                    <span aria-hidden className="icon-close" title="" />
                  </button>
                </span>
              )}
            </p>
            <div className="control">
              <button
                className="button is-rounded is-medium"
                id="keywords-search-button"
                type="submit"
              >
                Chercher
              </button>
            </div>
            <button
              type="button"
              className="button is-secondary"
              id="open-close-filter-menu-button"
              onClick={() => this.setState({ withFilter: !withFilter })}
            >
              &nbsp;
              <Icon
                svg={`ico-${withFilter ? 'chevron-up' : isfilterIconActive}`}
              />
              &nbsp;
            </button>
          </div>
        </form>

        <SearchFilter isVisible={withFilter} pagination={pagination} />

        <Switch location={location}>
          <Route
            exact
            path="/recherche"
            render={() => (
              <NavByOfferType pagination={pagination} title="PAR CATÉGORIES" />
            )}
          />
          <Route
            path="/recherche/resultats"
            render={() => (
              <SearchResults
                keywords={keywords}
                items={recommendations}
                loadMoreHandler={this.loadMoreHandler}
                pagination={pagination}
              />
            )}
          />
        </Switch>
      </Main>
    )
  }
}

SearchPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  pagination: PropTypes.object.isRequired,
  recommendations: PropTypes.array.isRequired,
  search: PropTypes.object.isRequired,
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withPagination({
    dataKey: 'recommendations',
    defaultWindowQuery: {
      categories: null,
      date: null,
      [mapApiToWindow.days]: null,
      [mapApiToWindow.search]: null,
      distance: null,
      latitude: null,
      longitude: null,
      orderBy: 'offer.id+desc',
    },
    windowToApiQuery,
  }),
  connect(state => ({
    recommendations: selectRecommendations(state),
    user: state.user,
  }))
)(SearchPage)
