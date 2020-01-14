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

class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      currentPage: 0,
      isLoading: false,
      resultsCount: 0,
      results: [],
      searchKeywords: '',
      totalPagesNumber: 0,
    }
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
    toast.info(
      "La recherche n'a pas pu aboutir, veuillez ré-essayer plus tard."
    )
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { currentPage, searchKeywords } = this.state
    const keywords = event.target.keywords.value
    const keywordsTrimmed = keywords.trim()

    if (searchKeywords === keywordsTrimmed) {
      return
    }

    if (keywordsTrimmed !== '') {
      if (searchKeywords !== keywordsTrimmed) {
        this.setState({
          currentPage: 0,
          results: [],
        }, () => {
          const { currentPage } = this.state
          this.handleFetchOffers(keywordsTrimmed, currentPage)
        })
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
    const { searchKeywords } = this.state
    this.fetchOffers(searchKeywords, currentPage)
  }

  fetchOffers = (keywords, currentPage) => {
    const { query } = this.props
    this.setState({
      isLoading: true,
    })

    fetch(keywords, currentPage).then(offers => {
      const { results } = this.state
      const { hits, nbHits, nbPages } = offers
      this.setState({
        currentPage: currentPage,
        isLoading: false,
        resultsCount: nbHits,
        results: [...results, ...hits],
        searchKeywords: keywords,
        totalPagesNumber: nbPages,
      })
      query.change({
        'mots-cles': keywords,
        page: currentPage + 1,
      })
    }).catch(() => {
      this.setState({
        isLoading: false
      })
      this.showFailModal()
    })
  }

  getScrollParent = () => document.querySelector('.sp-content')

  shouldBackFromDetails = () => {
    const { match } = this.props

    return Boolean(match.params.details)
  }

  render() {
    const { geolocation, location } = this.props
    const { search } = location
    const {
      currentPage,
      isLoading,
      resultsCount,
      results,
      searchKeywords,
      totalPagesNumber,
    } = this.state

    return (
      <main className="search-page">
        <HeaderContainer
          closeTitle="Retourner à la page découverte"
          closeTo="/decouverte"
          shouldBackFromDetails={this.shouldBackFromDetails()}
          title="Recherche"
        />
        <Switch>
          <Route
            exact
            path="/recherche-offres"
          >
            <div className="sp-content">
              <form onSubmit={this.handleOnSubmit}>
                <div className="sp-container">
                  <div className="sp-input-wrapper">
                    <input
                      className="sp-input"
                      defaultValue={searchKeywords}
                      name="keywords"
                      placeholder="Saisir un mot-clé"
                      type="text"
                    />
                  </div>
                  <button
                    className="sp-button"
                    type="submit"
                  >
                    {'Chercher'}
                  </button>
                </div>
              </form>
              {isLoading && <Spinner label="Recherche en cours" />}
              {searchKeywords && (
                <h1 className="sp-results-title">
                  {`"${searchKeywords}" : ${resultsCount} ${
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
            path="/recherche-offres/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?"
          >
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
}

export default SearchAlgolia
