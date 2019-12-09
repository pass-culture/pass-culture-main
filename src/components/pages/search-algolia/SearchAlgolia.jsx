import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'

import HeaderContainer from '../../layout/Header/HeaderContainer'
import ResultsContainer from './Results/ResultsContainer'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import SearchAlgoliaDetailsContainer from './SearchAlgoliaDetailsContainer/SearchAlgoliaDetailsContainer'
import Spinner from '../../layout/Spinner/Spinner'
import { fetch } from './utils/algoliaService'


class SearchAlgolia extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      backTo: null,
      isLoading: false,
      nbHits: 0,
      searchKeywords: null,
      searchResults: null,
    }
  }

  getShouldBackFromDetails = () => {
    const { match } = this.props
    const { params } = match
    const { details } = params
    if (details) {
      return true
    }
    return false
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const keywords = event.target.keywords.value

    if (keywords === null || keywords === '' ) {
      return null
    }

    const results = fetch(keywords)
    const { hits, nbHits } = results
    this.setState({
      backTo: '/recherche-algolia',
      isLoading: false,
      nbHits: nbHits,
      searchKeywords: keywords,
      searchResults: hits
    })
  }

  render() {
    const { backTo, isLoading, nbHits, searchKeywords, searchResults } = this.state

    return (
      <main className="search-page">
        <HeaderContainer
          backTo={backTo}
          closeTitle='Retourner à la page recherche'
          closeTo={'/recherche-algolia'}
          shouldBackFromDetails={this.getShouldBackFromDetails()}
          title="Recherche"
        />
        <Switch>
          <Route
            exact
            path="/recherche-algolia"
          >
            <div className="page-content">
              <form onSubmit={this.handleOnSubmit}>
                <div className="search-container">
                  <input
                    className="search-input"
                    name="keywords"
                    placeholder="Saisir un mot-clé"
                    type="text"
                  />
                  <button
                    className="search-button"
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
                <h2 className="results-title">
                  {`"${searchKeywords}" : ${nbHits} ${nbHits > 1 ? 'résultats' : 'résultat'}`}
                </h2>
              )}
              {searchResults && (
                <ResultsContainer searchResults={searchResults} />
              )}
            </div>
          </Route>

          <Route
            exact
            path="/recherche-algolia/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/:booking(reservation)?/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?"
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
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.str
    })
  }).isRequired,
}

export default SearchAlgolia
