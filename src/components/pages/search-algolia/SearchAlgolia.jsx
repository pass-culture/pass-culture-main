import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'

import HeaderContainer from '../../layout/Header/HeaderContainer'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import SearchAlgoliaDetailsContainer from './Result/ResultDetail/ResultDetailContainer'
import Spinner from '../../layout/Spinner/Spinner'
import { fetch } from './utils/algoliaService'
import Result from './Result/Result'
import PropTypes from 'prop-types'


class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: false,
      nbHits: 0,
      searchKeywords: '',
      hits: [],
    }
  }

  componentDidMount() {
    const { query } = this.props
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles']

    if (keywords != null) {
      this.getOffers(keywords)
    }
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const keywords = event.target.keywords.value

    if (keywords === '') {
      return null
    }
    this.getOffers(keywords)
  }

  getOffers = (keywords) => {
    this.setState({
      isLoading: true
    })
    const results = fetch(keywords)
    const { hits, nbHits } = results
    this.setState({
      isLoading: false,
      hits: hits,
      nbHits: nbHits,
      searchKeywords: keywords,
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
    parse: PropTypes.func
  }).isRequired
}

export default SearchAlgolia
