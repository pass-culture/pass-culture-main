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
import FiltersContainer from '../Filters/FiltersContainer'
import Result from './Result'
import SearchAlgoliaDetailsContainer from './ResultDetail/ResultDetailContainer'

class SearchResults extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      currentPage: 0,
      filters: {
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false
        },
        offerCategories: this.getCategoriesFromUrlOrProps(),
      },
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

  getCategoriesFromUrlOrProps() {
    const { query, categoriesFilter: categoriesFromProps } = this.props
    const queryParams = query.parse()
    const categoriesFromUrl = queryParams['categories'] || ''

    return categoriesFromUrl ? categoriesFromUrl.split(';') : categoriesFromProps
  }

  showFailModal = () => {
    toast.info("La recherche n'a pas pu aboutir, veuillez ré-essayer plus tard.")
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { history, query } = this.props
    const { searchedKeywords, filters } = this.state
    const { offerCategories } = filters
    const keywordsToSearch = event.target.keywords.value
    const trimmedKeywordsToSearch = keywordsToSearch.trim()

    const queryParams = query.parse()
    const autourDeMoi = queryParams['autour-de-moi']
    const tri = queryParams['tri']
    const categories = offerCategories.join(';')

    trimmedKeywordsToSearch &&
      history.replace({
        search: `?mots-cles=${trimmedKeywordsToSearch}&autour-de-moi=${autourDeMoi}&tri=${tri}&categories=${categories}`,
      })

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

  updateFilteredOffers = offers => {
    const { hits, nbHits, nbPages } = offers
    this.setState({
      currentPage: 0,
      resultsCount: nbHits,
      results: hits,
      totalPagesNumber: nbPages,
    })
  }

  updateFilters = filters => {
    this.setState({
      filters: filters,
    })
  }

  fetchOffers = (keywords, currentPage) => {
    const { geolocation, isSearchAroundMe, sortingIndexSuffix } = this.props
    const { filters } = this.state
    const { offerCategories, offerTypes } = filters
    this.setState({
      isLoading: true,
    })
    const geolocationCoordinates = isSearchAroundMe ? geolocation : null

    fetchAlgolia({
      categories: offerCategories,
      geolocationCoordinates,
      indexSuffix: sortingIndexSuffix,
      keywords,
      offerTypes,
      page: currentPage,
    }).then(offers => {
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
      }).catch(() => {
        this.setState({
          isLoading: false,
        })
        this.showFailModal()
    })
  }

  getScrollParent = () => document.querySelector('.sr-wrapper')

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

  getNumberOfResultsToDisplay = () => {
    const { searchedKeywords, resultsCount } = this.state
    const pluralizedResultatWord = resultsCount > 1 ? 'résultats' : 'résultat'
    const numberOfResults = `${resultsCount} ${pluralizedResultatWord}`

    return searchedKeywords ? `"${searchedKeywords}" : ${numberOfResults}` : numberOfResults
  }

  handleGoToFilters = () => {
    const { history } = this.props
    const { location } = history
    const { pathname, search } = location
    history.push(`${pathname}/filtres${search}`)
  }

  buildInitialFilters = () => {
    const { filters } = this.state
    const { query } = this.props
    const queryParams = query.parse()
    const autourDeMoi = queryParams['autour-de-moi']
    const sortCriteria = queryParams['tri']

    return {
      ...filters,
      isSearchAroundMe: autourDeMoi === 'oui',
      sortCriteria,
    }
  }

  render() {
    const { geolocation, history, match, query } = this.props
    const {
      currentPage,
      keywordsToSearch,
      isLoading,
      results,
      resultsCount,
      totalPagesNumber,
    } = this.state
    const { location } = history
    const { search } = location

    return (
      <main className="search-results-page">
        <Switch>
          <Route
            exact
            path="/recherche-offres/resultats(/menu)?"
          >
            <form
              action=""
              className="sr-form"
              onSubmit={this.handleOnSubmit}
            >
              <div className="sr-input-wrapper">
                <button
                  className="sr-input-back"
                  onClick={this.handleBackButtonClick}
                  type="button"
                >
                  <Icon
                    alt="Réinitialiser la recherche"
                    svg="picto-back-grey"
                  />
                </button>
                <input
                  className="sr-text-input"
                  name="keywords"
                  onChange={this.handleOnTextInputChange}
                  placeholder="Titre, artiste..."
                  ref={this.inputRef}
                  type="search"
                  value={keywordsToSearch}
                />
                <div className="sr-reset-wrapper">
                  {keywordsToSearch && (
                    <button
                      className="sr-reset"
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
            </form>
            <div className="sr-items-wrapper">
              <div className="sr-spinner">
                {isLoading && <Spinner label="Recherche en cours" />}
              </div>
              <h1 className="sr-items-number">
                {this.getNumberOfResultsToDisplay()}
              </h1>
              {results.length > 0 && (
                <InfiniteScroll
                  getScrollParent={this.getScrollParent}
                  hasMore={!isLoading && currentPage + 1 < totalPagesNumber}
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
            <div className="sr-filter-wrapper">
              <button
                className="sr-filter-button"
                onClick={this.handleGoToFilters}
                type="button"
              >
                <Icon
                  alt="Filtrer les résultats"
                  svg="filtrer"
                />
                <span>
                  {'Filtrer'}
                </span>
              </button>
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
          <Route path="/recherche-offres/resultats/filtres">
            <FiltersContainer
              history={history}
              initialFilters={this.buildInitialFilters()}
              match={match}
              offers={{
                hits: results,
                nbHits: resultsCount,
                nbPages: totalPagesNumber,
              }}
              query={query}
              showFailModal={this.showFailModal}
              updateFilteredOffers={this.updateFilteredOffers}
              updateFilters={this.updateFilters}
            />
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
  sortingIndexSuffix: '',
}

SearchResults.propTypes = {
  categoriesFilter: PropTypes.arrayOf(PropTypes.string),
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  history: PropTypes.shape().isRequired,
  isSearchAroundMe: PropTypes.bool,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
  sortingIndexSuffix: PropTypes.string,
}

export default SearchResults
