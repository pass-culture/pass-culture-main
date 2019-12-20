import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'

import HeaderContainer from '../../layout/Header/HeaderContainer'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import SearchAlgoliaDetailsContainer from './Result/ResultDetail/ResultDetailContainer'
import Spinner from '../../layout/Spinner/Spinner'
import { fetch } from './service/algoliaService'
import Result from './Result/Result'
import PropTypes from 'prop-types'


class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: false,
      hits: [],
      nbHits: 0,
      page: 0,
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

  handleFetchOffers = (keywords, page) => {
    if (page > 0) {
      this.getOffers(keywords, page - 1)
    } else {
      this.getOffers(keywords, 0)
    }
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { page } = this.state
    const keywords = event.target.keywords.value

    if (keywords !== '') {
      this.handleFetchOffers(keywords, page)
    }
  }

  getOffers = (keywords, page) => {
    const { query } = this.props
    this.setState({
      isLoading: true
    })

    const results = fetch(keywords, page)
    const { hits, nbHits } = results
    this.setState({
      isLoading: false,
      hits: hits,
      nbHits: nbHits,
      page: page,
      searchKeywords: keywords,
    })
    query.change({
      'mots-cles': keywords,
      'page': page + 1
    })
  }

  render() {
    const { geolocation } = this.props
    const { isLoading, nbHits, searchKeywords, hits } = this.state

    return (
      <main className="search-page">
        <HeaderContainer
          backTo={null}
          closeTitle='Retourner à la page recherche'
          closeTo='/decouverte'
          shouldBackFromDetails={false}
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
                  {`"${searchKeywords}" : ${nbHits} ${nbHits > 1 ? 'résultats' : 'résultat'}`}
                </h1>
              )}
              {hits.length > 0 && (
                hits.map((result) => (
                  <Result
                    geolocation={geolocation}
                    key={result.objectID}
                    result={result}
                  />
                ))
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
  query: PropTypes.shape({
    clear: PropTypes.func,
    change: PropTypes.func,
    parse: PropTypes.func
  }).isRequired
}

export default SearchAlgolia
