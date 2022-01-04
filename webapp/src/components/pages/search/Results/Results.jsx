import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { toast } from 'react-toastify'

import trackSearchKeyWords from '../../../../tracking/trackSearchKeyWords'
import { isGeolocationEnabled } from '../../../../utils/geolocation'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { DEFAULT_RADIUS_IN_KILOMETERS } from '../../../../vendor/algolia/filters'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import Spinner from '../../../layout/Spinner/Spinner'
import { Filters } from '../Filters/Filters'
import { DATE_FILTER, PRICE_FILTER, TIME_FILTER } from '../Filters/filtersEnums'
import Header from '../Header/Header'
import { EmptyResult } from './EmptyResult/EmptyResult'
import ResultDetailContainer from './ResultsList/ResultDetail/ResultDetailContainer'
import { ResultsList } from './ResultsList/ResultsList'

const SEARCH_RESULTS_URI = '/recherche/resultats'

class Results extends PureComponent {
  constructor(props) {
    super(props)
    const {
      criteria: { categories, searchAround },
      parametersFromHome,
      place,
    } = props
    const searchAroundFromUrlOrProps = this.getSearchAroundFromUrlOrProps(searchAround)
    const categoriesFromUrlOrProps = this.getCategoriesFromUrlOrProps(categories)
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
        offerIsFilteredByTime: false,
        date: {
          selectedDate: null,
          option: DATE_FILTER.TODAY.value,
        },
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: searchAroundFromUrlOrProps,
        timeRange: TIME_FILTER.DEFAULT_RANGE,
      },
      keywordsToSearch: '',
      isLoading: false,
      numberOfActiveFilters: this.getNumberOfActiveFilters(
        categoriesFromUrlOrProps,
        parametersFromHome,
        searchAroundFromUrlOrProps
      ),
      place: placeFromUrlOrProps,
      resultsCount: 0,
      results: [],
      searchedKeywords: '',
      totalPagesNumber: 0,
    }
    this.inputRef = React.createRef()
  }

  componentDidMount() {
    const { history, parametersFromHome, parse } = this.props
    const { currentPage } = this.state
    const queryParams = parse(history.location.search)
    const keywords = queryParams['mots-cles'] || ''

    if (parametersFromHome) {
      this.updateFiltersWhenComingFromHome(parametersFromHome, keywords, currentPage)
    } else {
      this.fetchOffers({ keywords, page: currentPage })
    }

    if (queryParams) {
      const categories = queryParams['categories']
      const keyWords = queryParams['mots-cles']
      trackSearchKeyWords(keyWords, categories)
    }
  }

  updateFiltersWhenComingFromHome = (parametersFromHome, keywords, currentPage) => {
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          ...parametersFromHome,
          searchAround: {
            everywhere: !parametersFromHome.searchAround,
            place: false,
            user: parametersFromHome.searchAround,
          },
        },
      },
      () => {
        this.fetchOffers({ keywords, page: currentPage })
      }
    )
  }

  getCategoriesFromUrlOrProps = categoriesFromProps => {
    const { history, parse } = this.props
    const queryParams = parse(history.location.search)
    const categoriesFromUrl = queryParams['categories'] || ''

    return categoriesFromUrl ? categoriesFromUrl.split(';') : categoriesFromProps
  }

  getPlaceFromUrlOrProps = placeFromUrlOrProps => {
    const { history, parse } = this.props
    const queryParams = parse(history.location.search)
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
    const { history, parse, userGeolocation } = this.props
    const queryParams = parse(history.location.search)
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
      const categoriesFromUrl = queryParams['categories'] || ''
      history.replace({
        search: `?mots-cles=${keywordsFromUrl}&autour-de=non&categories=${categoriesFromUrl}`,
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

  getNumberFromBoolean = boolean => (boolean === true ? 1 : 0)

  getPriceRangeCounter = priceRange => {
    const [lowestPrice, highestPrice] = priceRange
    const [defaultLowestPrice, defaultHighestPrice] = PRICE_FILTER.DEFAULT_RANGE
    return lowestPrice !== defaultLowestPrice || highestPrice !== defaultHighestPrice ? 1 : 0
  }

  getNumberOfSelectedFilters = filter => {
    let counter = 0

    Object.keys(filter).forEach(key => {
      if (filter[key] === true) {
        counter++
      }
    })
    return counter
  }

  getNumberOfActiveFilters = (categories, parametersFromHome, searchAround) => {
    const numberOfActiveCategories = categories.length
    const geolocationFilterCounter =
      searchAround.user === true || searchAround.place === true ? 1 : 0

    if (parametersFromHome) {
      const {
        offerCategories,
        offerIsDuo,
        offerIsFree,
        offerIsNew,
        offerTypes,
        priceRange,
      } = parametersFromHome

      return (
        geolocationFilterCounter +
        offerCategories.length +
        this.getNumberFromBoolean(offerIsDuo) +
        this.getNumberFromBoolean(offerIsFree) +
        this.getNumberFromBoolean(offerIsNew) +
        this.getNumberOfSelectedFilters(offerTypes) +
        this.getPriceRangeCounter(priceRange)
      )
    }
    return geolocationFilterCounter + numberOfActiveCategories
  }

  showFailModal = () => {
    toast.error("La recherche n'a pas pu aboutir, réessaie plus tard.")
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { history, parse } = this.props
    const { filters, searchedKeywords } = this.state
    const { offerCategories } = filters
    const keywordsToSearch = event.target.keywords.value
    const trimmedKeywordsToSearch = keywordsToSearch.trim()

    const queryParams = parse(history.location.search)
    const autourDe = queryParams['autour-de']
    const categories = offerCategories.join(';')
    const longitude = queryParams['longitude']
    const latitude = queryParams['latitude']
    const place = queryParams['place']

    const search =
      `?mots-cles=${trimmedKeywordsToSearch}` +
      `&autour-de=${autourDe}&categories=${categories}` +
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
    const { filters, place } = this.state
    const { userGeolocation } = this.props
    const {
      aroundRadius,
      date,
      offerIsFilteredByDate,
      offerIsFilteredByTime,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerIsNew,
      offerTypes,
      priceRange,
      searchAround,
      timeRange,
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
    }
    if (offerIsFilteredByDate) {
      options.date = date
    }
    if (offerIsFilteredByTime) {
      options.timeRange = timeRange
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

  handleOnScroll = () => {
    this.inputRef.current.blur()
  }

  handleGoTo = path => () => {
    const { history } = this.props
    const { pathname, search } = history.location
    history.push(`${pathname}/${path}${search}`)
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
        },
        place: null,
      },
      () => {
        if (isGeolocationEnabled(userGeolocation)) {
          history.push(
            `/recherche/resultats?mots-cles=&autour-de=oui&categories=&latitude=${userGeolocation.latitude}&longitude=${userGeolocation.longitude}`
          )
          this.fetchOffers()
        } else {
          window.alert('Active ta géolocalisation pour voir les offres autour de toi !')
        }
      }
    )
  }

  render() {
    const { history, match, parse, userGeolocation } = this.props
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
      totalPagesNumber,
    } = this.state
    const { geolocation: placeGeolocation } = place || {}
    const { searchAround } = filters
    const { location } = history
    const { search } = location
    const isSearchEmpty = !isLoading && results.length === 0

    return (
      <Fragment>
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
                results={results}
                resultsCount={resultsCount}
                search={search}
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
        <Switch>
          <Route
            path={`${SEARCH_RESULTS_URI}/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
          >
            <div className="offer-details">
              <HeaderContainer
                shouldBackFromDetails
                title="Recherche"
              />
              <ResultDetailContainer />
            </div>
          </Route>
          <Route path={`${SEARCH_RESULTS_URI}/filtres`}>
            <div className="offer-details">
              <Filters
                history={history}
                initialFilters={filters}
                match={match}
                nbHits={resultsCount}
                parse={parse}
                place={place}
                showFailModal={this.showFailModal}
                updateFilteredOffers={this.updateFilteredOffers}
                updateFilters={this.updateFilters}
                updateNumberOfActiveFilters={this.updateNumberOfActiveFilters}
                updatePlace={this.updatePlace}
                userGeolocation={userGeolocation}
              />
            </div>
          </Route>
        </Switch>
      </Fragment>
    )
  }
}

Results.defaultProps = {
  criteria: {
    categories: [],
    isSearchAroundMe: false,
  },
  parametersFromHome: null,
  place: {
    geolocation: { longitude: null, latitude: null },
    name: null,
  },
  userGeolocation: { longitude: null, latitude: null },
}

Results.propTypes = {
  criteria: PropTypes.shape({
    categories: PropTypes.arrayOf(PropTypes.string),
    searchAround: PropTypes.shape({
      everywhere: PropTypes.bool,
      place: PropTypes.bool,
      user: PropTypes.bool,
    }),
  }),
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  parametersFromHome: PropTypes.shape(),
  parse: PropTypes.func.isRequired,
  place: PropTypes.shape({
    geolocation: PropTypes.shape({
      latitude: PropTypes.number,
      longitude: PropTypes.number,
    }),
    name: PropTypes.string,
  }),
  redirectToSearchMainPage: PropTypes.func.isRequired,
  userGeolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
}

export default Results
