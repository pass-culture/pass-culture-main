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
    const keywords = queryParams['mots-cles']

    if (keywords != null) {
      const { currentPage } = this.state
      this.handleFetchOffers(keywords, currentPage)
    } else {
      query.clear()
    }
  }

  showFailModal = () => {
    toast.info("La recherche n'a pas pu aboutir, veuillez ré-essayer plus tard.")
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { currentPage, searchedKeywords } = this.state
    const keywords = event.target.keywords.value
    const keywordsTrimmed = keywords.trim()

    if (searchedKeywords === keywordsTrimmed) {
      return
    }

    if (keywordsTrimmed !== '') {
      if (searchedKeywords !== keywordsTrimmed) {
        this.setState(
          {
            currentPage: 0,
            results: [],
          },
          () => {
            const { currentPage } = this.state
            this.handleFetchOffers(keywordsTrimmed, currentPage)
          }
        )
      } else {
        this.handleFetchOffers(keywordsTrimmed, currentPage)
      }
    }
  }

  handleFetchOffers = (keywords, currentPage) => {
    if (currentPage > 0) {
      this.fetchOffers(keywords, currentPage - 1)
    } else {
      this.fetchOffers(keywords, 0)
    }
  }

  fetchNextOffersPage = currentPage => {
    const { searchedKeywords } = this.state
    this.fetchOffers(searchedKeywords, currentPage)
  }

  fetchOffers = (keywords, currentPage) => {
    const { categoriesFilter, geolocation, isSearchAroundMe } = this.props
    this.setState({
      isLoading: true,
    })
    const geolocationCoordinates = isSearchAroundMe ? geolocation : null

    fetchAlgolia(keywords, currentPage, geolocationCoordinates, categoriesFilter)
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

  render() {
    const { geolocation, search } = this.props
    const {
      currentPage,
      keywordsToSearch,
      isLoading,
      resultsCount,
      results,
      searchedKeywords,
      totalPagesNumber,
    } = this.state

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
                {searchedKeywords &&
                  `"${searchedKeywords}" : ${resultsCount} ${
                    resultsCount > 1 ? 'résultats' : 'résultat'
                  }`}
              </h1>
              {results.length > 0 && (
                <InfiniteScroll
                  getScrollParent={this.getScrollParent}
                  hasMore={currentPage + 1 < totalPagesNumber}
                  loader={<Spinner key="loader" />}
                  loadMore={this.fetchNextOffersPage}
                  pageStart={currentPage}
                  threshold={-10}
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
  isSearchAroundMe: PropTypes.bool,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
  search: PropTypes.string.isRequired,
}

export default SearchResults
