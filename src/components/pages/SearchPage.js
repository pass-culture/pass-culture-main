import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router-dom'
import { compose } from 'redux'

import { Icon, requestData, withLogin, withSearch } from 'pass-culture-shared'

import NavByOfferType from './search/NavByOfferType'
import SearchFilter from './search/SearchFilter'
import SearchResults from './search/SearchResults'
import Main from '../layout/Main'
import NavigationFooter from '../layout/NavigationFooter'
import { selectRecommendations } from '../../selectors'

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

const FRENCH_KEYWORDS_KEY = 'mots-cles'

class SearchPage extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      keywordsKey: 0,
      keywordsValue: get(props, `queryParams.${FRENCH_KEYWORDS_KEY}`),
    }
  }

  onSubmit = e => {
    const { handleQueryParamsChange, queryParams } = this.props

    e.preventDefault()

    if (
      !e.target.elements.keywords.value ||
      queryParams.keywords === e.target.elements.keywords.value
    ) {
      return
    }

    handleQueryParamsChange(
      { [FRENCH_KEYWORDS_KEY]: e.target.elements.keywords.value },
      { pathname: '/recherche/resultats' }
    )
  }

  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const {
      dispatch,
      goToNextSearchPage,
      location,
      match,
      querySearch,
    } = this.props

    dispatch(requestData('GET', 'types'))

    const len = get(location, 'search.length')
    if (!len) return

    const englishQuerySearch = querySearch
      .replace(`${FRENCH_KEYWORDS_KEY}=`, 'keywords=')
      .replace('categories=', 'types=')
      .replace('jours=', 'days=')

    dispatch(
      requestData('GET', `recommendations?${englishQuerySearch}`, {
        handleFail,
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          if (match.params.view === 'resultats' && !match.params.filtres) {
            goToNextSearchPage()
          }
        },
      })
    )
  }

  render() {
    const {
      handleQueryParamsChange,
      history,
      location,
      match,
      queryParams,
      querySearch,
      recommendations,
    } = this.props
    const { keywordsKey, keywordsValue } = this.state

    const keywords = queryParams[FRENCH_KEYWORDS_KEY]

    return (
      <Main
        backButton={
          match.params.view === 'resultats' && {
            onClick: () => history.push(`/recherche/categories?${querySearch}`),
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
                id="keywords"
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
                        // THE IN PUT WITH A SYNCED DEFAULT VALUE
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
                disabled={!keywordsValue || keywordsValue === keywords}
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
              onClick={() => {
                let pathname = `/recherche/${match.params.view}`
                if (!match.params.filtres) {
                  pathname = `${pathname}/filtres`
                }
                history.push(`${pathname}?${querySearch}`)
              }}
            >
              &nbsp;
              <Icon
                svg={`ico-${match.params.filtres ? 'chevron-up' : 'filter'}`}
              />
              &nbsp;
            </button>
          </div>
        </form>

        <Switch location={location}>
          <Route
            exact
            path="/recherche"
            render={() => <Redirect to="/recherche/categories" />}
          />
          <Route
            path="/recherche/:view/filtres"
            render={() => (
              <SearchFilter
                handleQueryParamsChange={handleQueryParamsChange}
                queryParams={queryParams}
              />
            )}
          />
          <Route
            path="/recherche/categories"
            render={() => (
              <NavByOfferType
                handleQueryParamsChange={handleQueryParamsChange}
                title="PAR CATEGORIES"
              />
            )}
          />
          <Route
            path="/recherche/resultats"
            render={() => (
              <Route
                path="/recherche/resultats"
                render={() => (
                  <SearchResults
                    keywords={keywords}
                    items={recommendations}
                    queryParams={queryParams}
                    loadMoreHandler={this.handleDataRequest}
                  />
                )}
              />
            )}
          />
        </Switch>
      </Main>
    )
  }
}

SearchPage.defaultProps = {
  querySearch: null,
}

SearchPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  goToNextSearchPage: PropTypes.func.isRequired,
  handleQueryParamsChange: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  queryParams: PropTypes.object.isRequired,
  querySearch: PropTypes.string,
  recommendations: PropTypes.array.isRequired,
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withSearch({
    dataKey: 'recommendations',
    defaultQueryParams: {
      [FRENCH_KEYWORDS_KEY]: null,
      date: null,
      days: null,
      distance: null,
      latitude: null,
      longitude: null,
      types: null,
    },
  }),
  connect(state => ({
    recommendations: selectRecommendations(state),
    user: state.user,
  }))
)(SearchPage)
