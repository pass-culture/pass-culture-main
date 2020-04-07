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
import { Criteria } from '../Criteria/Criteria'
import { SORT_CRITERIA } from '../Criteria/criteriaEnums'
import FiltersContainer from '../Filters/FiltersContainer'
import Result from './Result'
import SearchAlgoliaDetailsContainer from './ResultDetail/ResultDetailContainer'

const SEARCH_RESULTS_URI = '/recherche-offres/resultats'

class SearchResults extends PureComponent {
  constructor(props) {
    super(props)
    const {
      criteria: { categories, isSearchAroundMe, sortBy },
    } = props
    const sortByFromUrlOrProps = this.getSortByFromUrlOrProps(sortBy)

    this.state = {
      currentPage: 0,
      filters: {
        //radiusRevert: aroundRadius: 0,
        isSearchAroundMe: this.getIsSearchAroundMeFromUrlOrProps(isSearchAroundMe),
        offerCategories: this.getCategoriesFromUrlOrProps(categories),
        offerIsDuo: false,
        offerIsFree: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        sortBy: sortByFromUrlOrProps,
      },
      keywordsToSearch: '',
      isLoading: false,
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

  getSortByFromUrlOrProps = sortByFromProps => {
    const { query } = this.props
    const queryParams = query.parse()
    const sortByFromUrl = queryParams['tri'] || ''

    return sortByFromUrl ? sortByFromUrl : sortByFromProps
  }

  getScrollParent = () => document.querySelector('.sr-wrapper')

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

  fetchOffers = ({ keywords = '', page = 0 } = {}) => {
    const { geolocation } = this.props
    const { filters } = this.state
    const { aroundRadius, isSearchAroundMe, offerCategories, offerIsDuo, offerIsFree, offerTypes, sortBy } = filters

    this.setState({
      isLoading: true,
    })
    const options = {
      keywords,
      offerCategories,
      offerIsDuo,
      offerIsFree,
      offerTypes,
      page,
      sortBy,
    }

    if (isSearchAroundMe) {
      options.aroundRadius = aroundRadius
      options.geolocation = geolocation
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
    const { resultsCount } = this.state
    const pluralizedResultatWord = resultsCount > 1 ? 'résultats' : 'résultat'
    return `${resultsCount} ${pluralizedResultatWord}`
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

  render() {
    const { geolocation, history, match, query } = this.props
    const {
      currentPage,
      filters,
      keywordsToSearch,
      isLoading,
      results,
      resultsCount,
      sortCriterionLabel,
      totalPagesNumber,
    } = this.state
    const { location } = history
    const { search } = location

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
              <div className="sr-items-header">
                <span className="sr-items-number">
                  {this.getNumberOfResultsToDisplay()}
                </span>
                <button
                  className="sr-items-header-button"
                  onClick={this.handleGoTo('tri')}
                  type="button"
                >
                  <Icon svg="picto-sort" />
                  <span>
                    {sortCriterionLabel}
                  </span>
                </button>
              </div>
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
                onClick={this.handleGoTo('filtres')}
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
