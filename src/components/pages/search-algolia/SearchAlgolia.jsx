import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'

import HeaderContainer from '../../layout/Header/HeaderContainer'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import SearchAlgoliaDetailsContainer from './Result/ResultDetail/ResultDetailContainer'
import Spinner from '../../layout/Spinner/Spinner'
import { fetch } from './service/algoliaService'
import Result from './Result/Result'
import PropTypes from 'prop-types'
import InfiniteScroll from 'react-infinite-scroller'


class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: false,
      nbResults: 0,
      nbPages: 0,
      page: 0,
      results: [],
      searchKeywords: '',
    }
  }

  componentDidMount() {
    const { query } = this.props
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles']
    const page = queryParams['page']
    const pageAsInt = page ? parseInt(page) : 0

    if (keywords != null) {
      this.handleFetchOffers(keywords, pageAsInt)
    } else {
      query.clear()
    }
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { page, searchKeywords } = this.state
    const keywords = event.target.keywords.value
    const keywordsTrimmed = keywords.trim()

    if (keywordsTrimmed !== '') {

      if (searchKeywords !== keywordsTrimmed) {
        this.setState({
          results: []
        })
      }
      this.handleFetchOffers(keywordsTrimmed, page)
    }
  }

  handleFetchOffers = (keywords, page) => {
    if (page > 0) {
      this.getOffers(keywords, page - 1)
    } else {
      this.getOffers(keywords, 0)
    }
  }

  loadMore = page => {
    const { searchKeywords } = this.state
    this.getOffers(searchKeywords, page)
  }

  getOffers = (keywords, page) => {
    const { query } = this.props
    this.setState({
      isLoading: true
    })

    const response = fetch(keywords, page)
    response.then(offers => {
      const { results } = this.state
      const { hits, nbHits, nbPages } = offers
      this.setState({
        isLoading: false,
        nbPages: nbPages,
        nbResults: nbHits,
        page: page,
        results: [...results, ...hits],
        searchKeywords: keywords,
      })
      query.change({
        'mots-cles': keywords,
        'page': page + 1
      })
    })
  }

  getScrollParent = () => document.querySelector('.sp-content')

  shouldBackFromDetails = () => {
    const { match } = this.props
    const { params } = match
    const { details } = params

    return !!details
  }

  render() {
    const { geolocation, location } = this.props
    const { search } = location
    const { isLoading, nbResults, nbPages, page, results, searchKeywords } = this.state

    return (
      <main className="search-page">
        <HeaderContainer
          closeTitle='Retourner à la page découverte'
          closeTo='/decouverte'
          shouldBackFromDetails={this.shouldBackFromDetails()}
          title="Recherche"
        />
        <Switch>
          <Route
            exact
            path="/recherche-algolia"
          >
            <div className="sp-content">
              <form onSubmit={this.handleOnSubmit}>
                <div className="sp-container">
                  <input
                    className="sp-input"
                    defaultValue={searchKeywords}
                    name="keywords"
                    placeholder="Saisir un mot-clé"
                    type="text"
                  />
                  <button
                    className="sp-button"
                    type="submit"
                  >
                    {'Chercher'}
                  </button>
                </div>
              </form>
              {isLoading && (
                <Spinner
                  label="Recherche en cours"
                />
              )}
              {searchKeywords && (
                <h1 className="sp-result-title">
                  {`"${searchKeywords}" : ${nbResults} ${nbResults > 1 ? 'résultats' : 'résultat'}`}
                </h1>
              )}
              {results.length > 0 && (
                <InfiniteScroll
                  getScrollParent={this.getScrollParent}
                  hasMore={page + 1 < nbPages}
                  loader={<Spinner key="loader" />}
                  loadMore={this.loadMore}
                  pageStart={page}
                  threshold={-10}
                  useWindow={false}
                >
                  {results.map((result) => (
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
            path="/recherche-algolia/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?"
          >
            <SearchAlgoliaDetailsContainer />
          </Route>
        </Switch>
        <RelativeFooterContainer
          className="dotted-top-red"
          theme="white"
        />
      </main>
    )
  }
}

SearchAlgolia.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }).isRequired,
  location: PropTypes.shape({
    search: PropTypes.string
  }).isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func
  }).isRequired
}

export default SearchAlgolia
