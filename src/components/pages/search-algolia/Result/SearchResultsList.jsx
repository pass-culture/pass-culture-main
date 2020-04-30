import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import InfiniteScroll from 'react-infinite-scroller'
import { LOCALE_FRANCE } from "../../../../utils/date/date"
import Icon from '../../../layout/Icon/Icon'
import Result from './Result'

const getNumberOfResultsToDisplay = resultsCount => {
  const pluralizedResultatWord = resultsCount > 1 ? 'résultats' : 'résultat'
  return `${resultsCount.toLocaleString(LOCALE_FRANCE)} ${pluralizedResultatWord}`
}

export const SearchResultsList = ({
  currentPage,
  geolocation,
  isLoading,
  loadMore,
  onSortClick,
  results,
  resultsCount,
  search,
  sortCriterionLabel,
  totalPagesNumber,
}) => {
  return (
    <Fragment>
      <div className="sr-items-header">
        <span className="sr-items-number">
          {getNumberOfResultsToDisplay(resultsCount)}
        </span>
        <button
          className="sr-items-header-button"
          onClick={onSortClick}
          type="button"
        >
          <Icon svg="picto-sort" />
          <span>
            {sortCriterionLabel}
          </span>
        </button>
      </div>
      <InfiniteScroll
        hasMore={!isLoading && currentPage + 1 < totalPagesNumber}
        loadMore={loadMore}
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
    </Fragment>
  )
}

SearchResultsList.defaultProps = {
  search: '',
}
SearchResultsList.propTypes = {
  currentPage: PropTypes.number.isRequired,
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }).isRequired,
  isLoading: PropTypes.bool.isRequired,
  loadMore: PropTypes.func.isRequired,
  onSortClick: PropTypes.func.isRequired,
  results: PropTypes.arrayOf(
    PropTypes.shape({
      _geoloc: PropTypes.shape({
        lat: PropTypes.number,
        lng: PropTypes.number,
      }),
      offer: PropTypes.shape({
        dates: PropTypes.arrayOf(PropTypes.number),
        departementCode: PropTypes.number,
        id: PropTypes.string,
        isDuo: PropTypes.bool,
        label: PropTypes.string,
        name: PropTypes.string,
        prices: PropTypes.arrayOf(PropTypes.number),
        priceMin: PropTypes.number,
        priceMax: PropTypes.number,
        thumbUrl: PropTypes.string,
      }),
      objectID: PropTypes.string,
    })
  ).isRequired,
  resultsCount: PropTypes.number.isRequired,
  search: PropTypes.string,
  sortCriterionLabel: PropTypes.string.isRequired,
  totalPagesNumber: PropTypes.number.isRequired,
}
