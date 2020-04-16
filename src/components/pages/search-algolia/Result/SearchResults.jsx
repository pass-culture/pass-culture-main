import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { toast } from 'react-toastify'
import { isGeolocationEnabled } from '../../../../utils/geolocation'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import Spinner from '../../../layout/Spinner/Spinner'
import { Criteria } from '../Criteria/Criteria'
import { SORT_CRITERIA } from '../Criteria/criteriaEnums'
import FiltersContainer from '../Filters/FiltersContainer'
import { EmptySearchResult } from './EmptySearchResult'
import SearchAlgoliaDetailsContainer from './ResultDetail/ResultDetailContainer'
import { SearchResultsList } from './SearchResultsList'

const SEARCH_RESULTS_URI = '/recherche/resultats'

class SearchResults extends PureComponent {
  constructor(props) {
    super(props)
    const {
      criteria: { categories, isSearchAroundMe, sortBy },
    } = props
    const isSearchAroundMeFromUrlOrProps = this.getIsSearchAroundMeFromUrlOrProps(isSearchAroundMe)
    const categoriesFromUrlOrProps = this.getCategoriesFromUrlOrProps(categories)
    const sortByFromUrlOrProps = this.getSortByFromUrlOrProps(sortBy)

    this.state = {
      currentPage: 0,
      filters: {
        //radiusRevert: aroundRadius: 0,
        isSearchAroundMe: isSearchAroundMeFromUrlOrProps,
        offerCategories: categoriesFromUrlOrProps,
        offerIsDuo: false,
        offerIsFree: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        priceRange: [0, 500],
        sortBy: sortByFromUrlOrProps,
      },
      keywordsToSearch: '',
      isLoading: false,
      numberOfActiveFilters: this.getNumberOfActiveFilters(isSearchAroundMeFromUrlOrProps, categoriesFromUrlOrProps),
      resultsCount: 0,
      results: [],
      searchedKeywords: '',
      sortCriterionLabel: this.getSortCriterionLabelFromIndex(sortByFromUrlOrProps),
      totalPagesNumber: 0,
    }
    this.inputRef = React.createRef()
  }

  componentDidMount() {
    const { query } = this.props
    const { currentPage } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''
    this.fetchOffers({ keywords, page: currentPage })
  }

  getCategoriesFromUrlOrProps = categoriesFromProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const categoriesFromUrl = queryParams['categories'] || ''

    return categoriesFromUrl ? categoriesFromUrl.split(';') : categoriesFromProps
  }

  getIsSearchAroundMeFromUrlOrProps = isSearchAroundMeFromProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const isSearchAroundMeFromUrl = queryParams['autour-de-moi'] || ''

    return isSearchAroundMeFromUrl ? isSearchAroundMeFromUrl === 'oui' : isSearchAroundMeFromProps
  }

  getNumberOfActiveFilters = (isSearchAroundMe, categories) => {
    const numberOfActiveCategories = categories.length
    const geolocationFilterCounter = isSearchAroundMe === true ? 1 : 0
    return geolocationFilterCounter + numberOfActiveCategories
  }

  getSortByFromUrlOrProps = sortByFromProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const sortByFromUrl = queryParams['tri'] || ''

    return sortByFromUrl ? sortByFromUrl : sortByFromProps
  }

  showFailModal = () => {
    toast.info("La recherche n'a pas pu aboutir, veuillez ré-essayer plus tard.")
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { history, query } = this.props
    const { searchedKeywords, filters } = this.state
    const { offerCategories, sortBy: tri } = filters
    const keywordsToSearch = event.target.keywords.value
    const trimmedKeywordsToSearch = keywordsToSearch.trim()

    const queryParams = query.parse()
    const autourDeMoi = queryParams['autour-de-moi']
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
          this.fetchOffers({ keywords: trimmedKeywordsToSearch, page: currentPage })
        }
      )
    }
    this.inputRef.current.blur()
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

  updateNumberOfActiveFilters = numberOfFilters => {
    this.setState({
      numberOfActiveFilters: numberOfFilters,
    })
  }

  fetchOffers = ({ keywords = '', page = 0 } = {}) => {
    const { geolocation } = this.props
    const { filters } = this.state
    const {
      aroundRadius,
      isSearchAroundMe,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      priceRange,
      sortBy,
    } = filters

    this.setState({
      isLoading: true,
    })
    const options = {
      keywords,
      geolocation,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      page,
      priceRange,
      sortBy,
    }

    if (isSearchAroundMe) {
      options.aroundRadius = aroundRadius
    }

    fetchAlgolia(options)
      .then(offers => {
        const { results } = this.state
        const { hits, nbHits, nbPages } = offers
        this.setState({
          currentPage: page,
          keywordsToSearch: keywords,
          isLoading: false,
          resultsCount: nbHits,
          results: [...results, ...hits],
          searchedKeywords: keywords,
          sortCriterionLabel: this.getSortCriterionLabelFromIndex(sortBy),
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

  fetchNextOffers = currentPage => {
    const { searchedKeywords } = this.state
    this.fetchOffers({ keywords: searchedKeywords, page: currentPage })
  }

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

  blurInput = () => () => this.inputRef.current.blur()

  getSortCriterionLabelFromIndex(index) {
    const criterionLabels = Object.keys(SORT_CRITERIA).map(criterionKey => {
      return SORT_CRITERIA[criterionKey].index === index ? SORT_CRITERIA[criterionKey].label : ''
    })
    return criterionLabels.join('')
  }

  handleGoTo = path => () => {
    const { history } = this.props
    const { pathname, search } = history.location
    history.push(`${pathname}/${path}${search}`)
  }

  handleSortCriterionSelection = criterionKey => () => {
    const { searchedKeywords } = this.state
    const { history } = this.props
    const { search } = history.location
    const sortBy = SORT_CRITERIA[criterionKey].index
    this.setState(
      previousState => ({
        filters: { ...previousState.filters, sortBy: sortBy },
        results: [],
        sortCriterionLabel: this.getSortCriterionLabelFromIndex(sortBy),
      }),
      () => this.fetchOffers({ keywords: searchedKeywords })
    )
    const queryParams = search.replace(/(tri=)(\w*)/, 'tri=' + sortBy)

    history.push(`${SEARCH_RESULTS_URI}${queryParams}`)
  }

  handleNewSearchAroundMe = () => {
    const { geolocation, history } = this.props
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          offerCategories: [],
          isSearchAroundMe: true,
          sortBy: '',
        },
      },
      () => {
        if (isGeolocationEnabled(geolocation)) {
          history.push('/recherche/resultats?mots-cles=&autour-de-moi=oui&tri=&categories=')
          this.fetchOffers()
        } else {
          window.alert('Veuillez activer la géolocalisation pour voir les offres autour de vous.')
        }
      }
    )
  }

  render() {
    const { geolocation, history, match, query } = this.props
    const {
      currentPage,
      filters,
      keywordsToSearch,
      isLoading,
      numberOfActiveFilters,
      results,
      resultsCount,
      searchedKeywords,
      sortCriterionLabel,
      totalPagesNumber,
    } = this.state
    const { location } = history
    const { search } = location
    const isSearchEmpty = !isLoading && results.length === 0

    return (
      <main className="search-results-page">
        <Switch>
          <Route
            exact
            path={`${SEARCH_RESULTS_URI}(/menu)?`}
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
            <div
              className="sr-items-wrapper"
              onScroll={this.blurInput()}
            >
              <div className="sr-spinner">
                {isLoading && <Spinner label="Recherche en cours" />}
              </div>
              {isSearchEmpty && (
                <EmptySearchResult
                  onNewSearchAroundMe={this.handleNewSearchAroundMe}
                  searchedKeywords={searchedKeywords}
                />
              )}
              {results.length > 0 && (
                <SearchResultsList
                  currentPage={currentPage}
                  geolocation={geolocation}
                  isLoading={isLoading}
                  loadMore={this.fetchNextOffers}
                  onSortClick={this.handleGoTo('tri')}
                  results={results}
                  resultsCount={resultsCount}
                  search={search}
                  sortCriterionLabel={sortCriterionLabel}
                  totalPagesNumber={totalPagesNumber}
                />
              )}
            </div>
            {!isSearchEmpty && (
              <div className="sr-filter-wrapper">
                <button
                  className="sr-filter-button"
                  onClick={this.handleGoTo('filtres')}
                  type="button"
                >
                  <Icon
                    alt="Filtrer les résultats"
                    svg="filtrer"
                  />
                  <span className="sr-filter-button-text">
                    {'Filtrer'}
                  </span>
                  {numberOfActiveFilters > 0 && (
                    <span
                      className="sr-filter-button-counter"
                      data-test="sr-filter-button-counter"
                    >
                      {numberOfActiveFilters}
                    </span>
                  )}
                </button>
              </div>
            )}
          </Route>
          <Route
            path={`${SEARCH_RESULTS_URI}/:details(details|transition)/:offerId([A-Z0-9]+)(/menu)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
          >
            <HeaderContainer
              closeTitle="Retourner à la page découverte"
              closeTo="/decouverte"
              shouldBackFromDetails={this.shouldBackFromDetails()}
              title="Recherche"
            />
            <SearchAlgoliaDetailsContainer />
          </Route>
          <Route path={`${SEARCH_RESULTS_URI}/filtres`}>
            <FiltersContainer
              history={history}
              initialFilters={filters}
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
              updateNumberOfActiveFilters={this.updateNumberOfActiveFilters}
            />
          </Route>
          <Route path={`${SEARCH_RESULTS_URI}/tri`}>
            <Criteria
              activeCriterionLabel={sortCriterionLabel}
              backTo={`${SEARCH_RESULTS_URI}${search}`}
              criteria={SORT_CRITERIA}
              history={history}
              match={match}
              onCriterionSelection={this.handleSortCriterionSelection}
              title="Trier par"
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
  criteria: {
    categories: [],
    isSearchAroundMe: false,
    sortBy: '',
  },
  geolocation: { longitude: null, latitude: null },
}

SearchResults.propTypes = {
  criteria: PropTypes.shape({
    categories: PropTypes.array,
    isSearchAroundMe: PropTypes.bool,
    sortBy: PropTypes.string,
  }),
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  query: PropTypes.shape({
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
}

export default SearchResults
