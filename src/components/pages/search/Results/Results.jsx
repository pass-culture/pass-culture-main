import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { toast } from 'react-toastify'

import { isGeolocationEnabled } from '../../../../utils/geolocation'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { DEFAULT_RADIUS_IN_KILOMETERS } from '../../../../vendor/algolia/filters'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import Spinner from '../../../layout/Spinner/Spinner'
import { SORT_CRITERIA } from '../Criteria/criteriaEnums'
import CriteriaSort from '../CriteriaSort/CriteriaSort'
import { Filters } from '../Filters/Filters'
import { DATE_FILTER, PRICE_FILTER, TIME_FILTER } from '../Filters/filtersEnums'
import { EmptyResult } from './EmptyResult/EmptyResult'
import ResultDetailContainer from './ResultsList/ResultDetail/ResultDetailContainer'
import { ResultsList } from './ResultsList/ResultsList'
import Header from '../Header/Header'

const SEARCH_RESULTS_URI = '/recherche/resultats'

class Results extends PureComponent {
  constructor(props) {
    super(props)
    const {
      criteria: { categories, searchAround, sortBy },
      place,
    } = props
    const searchAroundFromUrlOrProps = this.getSearchAroundFromUrlOrProps(searchAround)
    const categoriesFromUrlOrProps = this.getCategoriesFromUrlOrProps(categories)
    const sortByFromUrlOrProps = this.getSortByFromUrlOrProps(sortBy)
    const placeFromUrlOrProps = this.getPlaceFromUrlOrProps(place)

    this.state = {
      currentPage: 0,
      filters: {
        aroundRadius: DEFAULT_RADIUS_IN_KILOMETERS,
        offerCategories: categoriesFromUrlOrProps,
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        offerIsFilteredByDate: false,
        date: {
          selectedDate: null,
          option: DATE_FILTER.TODAY.value,
        },
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: searchAroundFromUrlOrProps,
        sortBy: sortByFromUrlOrProps,
        timeRange: TIME_FILTER.DEFAULT_RANGE,
      },
      keywordsToSearch: '',
      isLoading: false,
      numberOfActiveFilters: this.getNumberOfActiveFilters(
        categoriesFromUrlOrProps,
        searchAroundFromUrlOrProps
      ),
      place: placeFromUrlOrProps,
      resultsCount: 0,
      results: [],
      scrollPosition: 0,
      searchedKeywords: '',
      shouldGoBackToScrollPosition: false,
      sortCriterionLabel: this.getSortCriterionLabelFromIndex(sortByFromUrlOrProps),
      totalPagesNumber: 0,
      userGeolocation: props.userGeolocation,
    }
    this.inputRef = React.createRef()
    this.scrollRef = React.createRef()
  }

  componentDidMount() {
    const { query } = this.props
    const { currentPage } = this.state
    const queryParams = query.parse()
    const keywords = queryParams['mots-cles'] || ''
    this.fetchOffers({ keywords, page: currentPage })
  }

  componentDidUpdate() {
    const { shouldGoBackToScrollPosition, scrollPosition } = this.state
    const scrollRef = this.scrollRef.current

    if (shouldGoBackToScrollPosition && scrollRef) {
      scrollRef.scrollTo(0, scrollPosition)
      // eslint-disable-next-line react/no-did-update-set-state
      this.setState({ shouldGoBackToScrollPosition: false })
    }
  }

  retrieveScrollPosition = () => {
    this.setState({ shouldGoBackToScrollPosition: true })
  }

  getCategoriesFromUrlOrProps = categoriesFromProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const categoriesFromUrl = queryParams['categories'] || ''

    return categoriesFromUrl ? categoriesFromUrl.split(';') : categoriesFromProps
  }

  getPlaceFromUrlOrProps = placeFromUrlOrProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const latitudeFromUrl = queryParams['latitude']
    const longitudeFromUrl = queryParams['longitude']
    const placeFromUrl = queryParams['place']

    if (latitudeFromUrl && longitudeFromUrl && placeFromUrl) {
      const splittedPlace = placeFromUrl.split(',')

      return {
        geolocation: { latitude: latitudeFromUrl, longitude: longitudeFromUrl },
        name: {
          long: placeFromUrl,
          short: splittedPlace[0],
        },
      }
    } else {
      return placeFromUrlOrProps
    }
  }

  getSearchAroundFromUrlOrProps = searchAroundFromProps => {
    const { history, query, userGeolocation } = this.props
    const queryParams = query.parse()
    const searchAroundFromUrl = queryParams['autour-de'] || ''
    const latitudeFromUrl = queryParams['latitude']
    const longitudeFromUrl = queryParams['longitude']
    const placeFromUrl = queryParams['place']

    if (searchAroundFromUrl === 'oui') {
      if (placeFromUrl && latitudeFromUrl && longitudeFromUrl) {
        return {
          everywhere: false,
          place: true,
          user: false,
        }
      }
      if (isGeolocationEnabled(userGeolocation)) {
        return {
          everywhere: false,
          place: false,
          user: true,
        }
      }
      const keywordsFromUrl = queryParams['mots-cles'] || ''
      const sortByFromUrl = queryParams['tri'] || ''
      const categoriesFromUrl = queryParams['categories'] || ''
      history.replace({
        search: `?mots-cles=${keywordsFromUrl}&autour-de=non&tri=${sortByFromUrl}&categories=${categoriesFromUrl}`,
      })
      return {
        everywhere: true,
        place: false,
        user: false,
      }
    } else {
      return searchAroundFromProps
    }
  }

  getNumberOfActiveFilters = (categories, searchAround) => {
    const numberOfActiveCategories = categories.length
    const geolocationFilterCounter =
      searchAround.user === true || searchAround.place === true ? 1 : 0
    return geolocationFilterCounter + numberOfActiveCategories
  }

  getSortByFromUrlOrProps = sortByFromProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const sortByFromUrl = queryParams['tri'] || ''

    return sortByFromUrl ? sortByFromUrl : sortByFromProps
  }

  showFailModal = () => {
    toast.error("La recherche n'a pas pu aboutir, réessaie plus tard.")
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { history, query } = this.props
    const { filters, searchedKeywords } = this.state
    const { offerCategories, sortBy: tri } = filters
    const keywordsToSearch = event.target.keywords.value
    const trimmedKeywordsToSearch = keywordsToSearch.trim()

    const queryParams = query.parse()
    const autourDe = queryParams['autour-de']
    const categories = offerCategories.join(';')
    const longitude = queryParams['longitude']
    const latitude = queryParams['latitude']
    const place = queryParams['place']

    const search =
      `?mots-cles=${trimmedKeywordsToSearch}` +
      `&autour-de=${autourDe}&tri=${tri}&categories=${categories}` +
      `&latitude=${latitude}` +
      `&longitude=${longitude}` +
      `${place ? `&place=${place}` : ''}`

    history.replace({
      search: search,
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

  updatePlace = place => {
    this.setState({
      place,
    })
  }

  updateNumberOfActiveFilters = numberOfFilters => {
    this.setState({
      numberOfActiveFilters: numberOfFilters,
    })
  }

  fetchOffers = ({ keywords = '', page = 0 } = {}) => {
    const { filters, place, userGeolocation } = this.state
    const {
      aroundRadius,
      date,
      offerIsFilteredByDate,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerIsNew,
      offerTypes,
      priceRange,
      searchAround,
      sortBy,
    } = filters

    this.setState({
      isLoading: true,
    })
    const options = {
      aroundRadius,
      keywords,
      geolocation: searchAround.place ? place.geolocation : userGeolocation,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerIsNew,
      offerTypes,
      page,
      priceRange,
      searchAround: searchAround.everywhere !== true,
      sortBy,
    }

    if (offerIsFilteredByDate) {
      options.date = date
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

  handleOnScroll = event => {
    this.inputRef.current.blur()
    this.rememberScrollPosition(event.target)
  }

  rememberScrollPosition = eventTarget => {
    const { scrollPosition: previousScrollPosition } = this.state
    const resultHeight = 100

    const currentScrollPosition = eventTarget.scrollTop
    const distance = currentScrollPosition - previousScrollPosition
    const scrollHeight = Math.sign(distance) * distance

    if (scrollHeight > resultHeight) {
      this.setState({ scrollPosition: currentScrollPosition })
    }
  }

  getSortCriterionLabelFromIndex = index => {
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

  handleSortCriterionSelection = criterionKey => {
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
    const { history, userGeolocation } = this.props
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          offerCategories: [],
          searchAround: {
            everywhere: false,
            place: false,
            user: true,
          },
          sortBy: '',
        },
        place: null,
      },
      () => {
        if (isGeolocationEnabled(userGeolocation)) {
          history.push(
            `/recherche/resultats?mots-cles=&autour-de=oui&tri=&categories=&latitude=${userGeolocation.latitude}&longitude=${userGeolocation.longitude}`
          )
          this.fetchOffers()
        } else {
          window.alert('Active ta géolocalisation pour voir les offres autour de toi !')
        }
      }
    )
  }

  render() {
    const { history, match, query, userGeolocation } = this.props
    const {
      currentPage,
      filters,
      keywordsToSearch,
      isLoading,
      numberOfActiveFilters,
      place,
      results,
      resultsCount,
      searchedKeywords,
      sortCriterionLabel,
      totalPagesNumber,
    } = this.state
    const { geolocation: placeGeolocation } = place || {}
    const { searchAround } = filters
    const { location } = history
    const { search } = location
    const isSearchEmpty = !isLoading && results.length === 0

    return (
      <Switch>
        <Route
          exact
          path={SEARCH_RESULTS_URI}
        >
          <main className="search-results-page">
            <Header
              onBackButtonClick={this.handleBackButtonClick}
              onResetClick={this.handleResetButtonClick}
              onSearchChange={this.handleOnTextInputChange}
              onSubmit={this.handleOnSubmit}
              ref={this.inputRef}
              value={keywordsToSearch}
            />
            <div
              className="sr-items-wrapper"
              onScroll={this.handleOnScroll}
              ref={this.scrollRef}
            >
              <div className="sr-spinner">
                {isLoading && <Spinner label="Recherche en cours" />}
              </div>
              {isSearchEmpty && (
                <EmptyResult
                  onNewSearchAroundMe={this.handleNewSearchAroundMe}
                  searchedKeywords={searchedKeywords}
                />
              )}
              {results.length > 0 && (
                <ResultsList
                  currentPage={currentPage}
                  geolocation={searchAround.place ? placeGeolocation : userGeolocation}
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
          </main>
        </Route>
        <Route
          path={`${SEARCH_RESULTS_URI}/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
        >
          <HeaderContainer
            backActionOnClick={this.retrieveScrollPosition}
            shouldBackFromDetails={this.shouldBackFromDetails()}
            title="Recherche"
          />
          <ResultDetailContainer />
        </Route>
        <Route path={`${SEARCH_RESULTS_URI}/filtres`}>
          <Filters
            history={history}
            initialFilters={filters}
            match={match}
            offers={{
              hits: results,
              nbHits: resultsCount,
              nbPages: totalPagesNumber,
            }}
            place={place}
            query={query}
            showFailModal={this.showFailModal}
            updateFilteredOffers={this.updateFilteredOffers}
            updateFilters={this.updateFilters}
            updateNumberOfActiveFilters={this.updateNumberOfActiveFilters}
            updatePlace={this.updatePlace}
            userGeolocation={userGeolocation}
          />
        </Route>
        <Route path={`${SEARCH_RESULTS_URI}/tri`}>
          <CriteriaSort
            activeCriterionLabel={sortCriterionLabel}
            backTo={`${SEARCH_RESULTS_URI}${search}`}
            criteria={SORT_CRITERIA}
            geolocation={searchAround.place ? placeGeolocation : userGeolocation}
            history={history}
            match={match}
            onCriterionSelection={this.handleSortCriterionSelection}
            title="Trier par"
          />
        </Route>
      </Switch>
    )
  }
}

Results.defaultProps = {
  criteria: {
    categories: [],
    isSearchAroundMe: false,
    sortBy: '',
  },
  place: {
    geolocation: { longitude: null, latitude: null },
    name: null,
  },
  userGeolocation: { longitude: null, latitude: null },
}

Results.propTypes = {
  criteria: PropTypes.shape({
    categories: PropTypes.array,
    searchAround: PropTypes.shape({
      everywhere: PropTypes.bool,
      place: PropTypes.bool,
      user: PropTypes.bool,
    }),
    sortBy: PropTypes.string,
  }),
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  place: PropTypes.shape({
    geolocation: PropTypes.shape({
      latitude: PropTypes.number,
      longitude: PropTypes.number,
    }),
    name: PropTypes.string,
  }),
  query: PropTypes.shape({
    parse: PropTypes.func,
  }).isRequired,
  redirectToSearchMainPage: PropTypes.func.isRequired,
  userGeolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
}

export default Results
