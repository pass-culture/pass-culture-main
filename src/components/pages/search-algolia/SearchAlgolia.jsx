import InfiniteScroll from 'react-infinite-scroller'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { toast } from 'react-toastify'

import { fetch } from './service/algoliaService'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import SearchAlgoliaDetailsContainer from './Result/ResultDetail/ResultDetailContainer'
import Spinner from '../../layout/Spinner/Spinner'
import Result from './Result/Result'
import { computeToAroundLatLng } from '../../../utils/geolocation'
import Icon from '../../layout/Icon/Icon'

class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      currentPage: 0,
      keywordsToSearch: '',
      hasSearchBeenMade: false,
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
    const page = queryParams['page']
    const currentPage = page ? parseInt(page) : 0

    if (keywords != null) {
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
    const { geolocation, query } = this.props
    this.setState({
      isLoading: true,
    })
    const aroundLatLng = computeToAroundLatLng(geolocation)

    fetch(keywords, currentPage, aroundLatLng)
      .then(offers => {
        const { results } = this.state
        const { hits, nbHits, nbPages } = offers
        this.setState({
          currentPage: currentPage,
          keywordsToSearch: keywords,
          hasSearchBeenMade: true,
          isLoading: false,
          resultsCount: nbHits,
          results: [...results, ...hits],
          searchedKeywords: keywords,
          totalPagesNumber: nbPages,
        })
        query.change({
          'mots-cles': keywords,
          page: currentPage + 1,
        })
      })
      .catch(() => {
        this.setState({
          isLoading: false,
        })
        this.showFailModal()
      })
  }

  getScrollParent = () => document.querySelector('.sp-results-wrapper')

  handleBackButtonClick = () => {
    const { redirectToSearchMainPage } = this.props
    this.setState({
      currentPage: 0,
      keywordsToSearch: '',
      hasSearchBeenMade: false,
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
    const { geolocation, location } = this.props
    const { search } = location
    const {
      currentPage,
      keywordsToSearch,
      hasSearchBeenMade,
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
            path="/recherche-offres"
          >
            {!hasSearchBeenMade && (
              <HeaderContainer
                closeTitle="Retourner à la page découverte"
                closeTo="/decouverte"
                extraClassName="header-search-main-page"
                shouldBackFromDetails={this.shouldBackFromDetails()}
                title="Recherche"
              />
            )}
            <form
              className="sp-text-input-form"
              onSubmit={this.handleOnSubmit}
            >
              <div className="sp-text-input-wrapper">
                {hasSearchBeenMade ? (
                  <button
                    className="sp-text-input-back"
                    onClick={this.handleBackButtonClick}
                    type="button"
                  >
                    <Icon svg="picto-back-grey" />
                  </button>
                ) : (
                  <div className="sp-text-input-back">
                    <Icon svg="picto-search" />
                  </div>
                )}
                <input
                  className="sp-text-input"
                  name="keywords"
                  onChange={this.handleOnTextInputChange}
                  placeholder="Artiste, auteur..."
                  ref={this.inputRef}
                  type="text"
                  value={keywordsToSearch}
                />
                <div className="sp-text-input-reset">
                  {keywordsToSearch && (
                    <button
                      className="sp-text-input-reset-button"
                      onClick={this.handleResetButtonClick}
                      type="reset"
                    >
                      <Icon svg="picto-reset" />
                    </button>
                  )}
                </div>
              </div>
              <div className="sp-search-button-wrapper">
                <button
                  className={`sp-search-button ${
                    hasSearchBeenMade ? 'sp-minimize-search-button' : ''
                  }`}
                  type="submit"
                >
                  {'Rechercher'}
                </button>
              </div>
            </form>

            <div className="sp-results-wrapper">
              {isLoading && <Spinner label="Recherche en cours" />}
              {hasSearchBeenMade && (
                <h1 className="sp-results-title">
                  {`"${searchedKeywords}" : ${resultsCount} ${
                    resultsCount > 1 ? 'résultats' : 'résultat'
                  }`}
                </h1>
              )}
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
          <Route
            exact
            path="/recherche-offres/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
            sensitive
          >
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

SearchAlgolia.defaultProps = {
  geolocation: {},
}

SearchAlgolia.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  location: PropTypes.shape({
    search: PropTypes.string,
  }).isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
}

export default SearchAlgolia
