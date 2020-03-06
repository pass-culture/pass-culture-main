import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import InfiniteScroll from 'react-infinite-scroller'
import { Route, Switch } from 'react-router'
import { toast } from 'react-toastify'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import Spinner from '../../../layout/Spinner/Spinner'
import Result from './Result'
import SearchAlgoliaDetailsContainer from './ResultDetail/ResultDetailContainer'

class SearchResults extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      currentPage: 0,
      keywordsToSearch: '',
      isLoading: false,
      resultsCount: 0,
      results: [],
      searchedKeywords: '',
      totalPagesNumber: 0,
    }
    this.inputRef = React.createRef()
  }

  componentDidMount() {
    const { query } = this.props
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''

    const { currentPage } = this.state
    this.fetchOffers(keywords, currentPage)
  }

  showFailModal = () => {
    toast.info("La recherche n'a pas pu aboutir, veuillez ré-essayer plus tard.")
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { history } = this.props
    const { searchedKeywords } = this.state
    const keywordsToSearch = event.target.keywords.value
    const trimmedKeywordsToSearch = keywordsToSearch.trim()
    trimmedKeywordsToSearch && history.replace({ search: '?mots-cles=' + trimmedKeywordsToSearch })

    if (searchedKeywords !== trimmedKeywordsToSearch) {
      this.setState(
        {
          currentPage: 0,
          results: [],
        },
        () => {
          const { currentPage } = this.state
          this.fetchOffers(trimmedKeywordsToSearch, currentPage)
        }
      )
    }
  }

  fetchNextOffers = currentPage => {
    const { searchedKeywords } = this.state
    this.fetchOffers(searchedKeywords, currentPage)
  }

  fetchOffers = (keywords, currentPage) => {
    const { categoriesFilter, geolocation, isSearchAroundMe , sortingIndexSuffix } = this.props
    this.setState({
      isLoading: true,
    })
    const geolocationCoordinates = isSearchAroundMe ? geolocation : null

    fetchAlgolia(keywords, currentPage, geolocationCoordinates, categoriesFilter, sortingIndexSuffix)
      .then(offers => {
        const { results } = this.state
        const { hits, nbHits, nbPages } = offers
        this.setState({
          currentPage: currentPage,
          keywordsToSearch: keywords,
          isLoading: false,
          resultsCount: nbHits,
          results: [...results, ...hits],
          searchedKeywords: keywords,
          totalPagesNumber: nbPages,
        })
      })
      .catch(() => {
        this.setState({
          isLoading: false,
        })
        this.showFailModal()
      })
  }

  getScrollParent = () => document.querySelector('.home-results-wrapper')

  handleBackButtonClick = () => {
    const { redirectToSearchMainPage } = this.props
    this.setState({
      currentPage: 0,
      keywordsToSearch: '',
      isLoading: false,
      resultsCount: 0,
      results: [],
      searchedKeywords: '',
      totalPagesNumber: 0,
    })
    redirectToSearchMainPage()
  }

  shouldBackFromDetails = () => {
    const { match } = this.props

    return Boolean(match.params.details)
  }

  handleResetButtonClick = () => {
    this.setState({
      keywordsToSearch: '',
    })
    this.inputRef.current.focus()
  }

  handleOnTextInputChange = event => {
    this.setState({
      keywordsToSearch: event.target.value,
    })
  }

  getNumberOfResultsToDisplay() {
    const { searchedKeywords, resultsCount } = this.state
    const pluralizedResultatWord = resultsCount > 1 ? 'résultats' : 'résultat'
    const numberOfResults = `${resultsCount} ${pluralizedResultatWord}`

    return searchedKeywords ? `"${searchedKeywords}" : ${numberOfResults}` : numberOfResults
  }

  render() {
    const {
      geolocation,
      history: { search },
    } = this.props
    const { currentPage, keywordsToSearch, isLoading, results, totalPagesNumber } = this.state

    return (
      <main className="search-page-algolia">
        <Switch>
          <Route
            exact
            path="/recherche-offres/resultats(/menu)?"
          >
            <form
              className="spr-text-input-form"
              onSubmit={this.handleOnSubmit}
            >
              <div className="home-text-input-wrapper">
                <button
                  className="home-text-input-back"
                  onClick={this.handleBackButtonClick}
                  type="button"
                >
                  <Icon
                    alt="Réinitialiser la recherche"
                    svg="picto-back-grey"
                  />
                </button>
                <input
                  className="home-text-input"
                  name="keywords"
                  onChange={this.handleOnTextInputChange}
                  placeholder="Artiste, auteur..."
                  ref={this.inputRef}
                  type="text"
                  value={keywordsToSearch}
                />
                <div className="home-text-input-reset">
                  {keywordsToSearch && (
                    <button
                      className="home-text-input-reset-button"
                      onClick={this.handleResetButtonClick}
                      type="reset"
                    >
                      <Icon
                        alt="Supprimer la saisie"
                        svg="picto-reset"
                      />
                    </button>
                  )}
                </div>
              </div>
              <div className="home-search-button-wrapper">
                <button
                  className="home-search-button home-minimize-search-button"
                  type="submit"
                >
                  {'Rechercher'}
                </button>
              </div>
            </form>

            <div className="home-results-wrapper">
              {isLoading && <Spinner label="Recherche en cours" />}
              <h1 className="home-results-title">
                {this.getNumberOfResultsToDisplay()}
              </h1>
              {results.length > 0 && (
                <InfiniteScroll
                  getScrollParent={this.getScrollParent}
                  hasMore={!isLoading && (currentPage + 1 < totalPagesNumber)}
                  loader={<Spinner key="loader" />}
                  loadMore={this.fetchNextOffers}
                  pageStart={currentPage}
                  threshold={100}
                  useWindow={false}
                >
                  {results.map(result => (
                    <Result
                      geolocation={geolocation}
                      key={result.objectID}
                      result={result}
                      search={search}
                    />
                  ))}
                </InfiniteScroll>
              )}
            </div>
          </Route>
          <Route path="/recherche-offres/resultats/:details(details|transition)/:offerId([A-Z0-9]+)(/menu)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?">
            <HeaderContainer
              closeTitle="Retourner à la page découverte"
              closeTo="/decouverte"
              shouldBackFromDetails={this.shouldBackFromDetails()}
              title="Recherche"
            />
            <SearchAlgoliaDetailsContainer />
          </Route>
        </Switch>

        <RelativeFooterContainer
          extraClassName="dotted-top-red"
          theme="white"
        />
      </main>
    )
  }
}

SearchResults.defaultProps = {
  categoriesFilter: [],
  geolocation: { longitude: null, latitude: null },
  isSearchAroundMe: false,
}

SearchResults.propTypes = {
  categoriesFilter: PropTypes.arrayOf(PropTypes.string),
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  isSearchAroundMe: PropTypes.bool,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
  search: PropTypes.string.isRequired,
  sortingIndexSuffix: PropTypes.string.isRequired,
}

export default SearchResults
