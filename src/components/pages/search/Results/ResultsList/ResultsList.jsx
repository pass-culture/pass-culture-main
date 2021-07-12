import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import InfiniteScroll from 'react-infinite-scroller'
import { LOCALE_FRANCE } from '../../../../../utils/date/date'
import Result from './Result/Result'

const getNumberOfResultsToDisplay = resultsCount => {
  const pluralizedResultatWord = resultsCount > 1 ? 'résultats' : 'résultat'
  return `${resultsCount.toLocaleString(LOCALE_FRANCE)} ${pluralizedResultatWord}`
}

export const ResultsList = ({
  currentPage,
  geolocation,
  isLoading,
  loadMore,
  results,
  resultsCount,
  search,
  totalPagesNumber,
}) => {
  return (
    <Fragment>
      <div className="sr-items-header">
        <span className="sr-items-number">
          {getNumberOfResultsToDisplay(resultsCount)}
        </span>
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

export const SearchHit = {
  offer: PropTypes.shape({
    dates: PropTypes.arrayOf(PropTypes.number),
    id: PropTypes.string,
    isDigital: PropTypes.bool,
    isDuo: PropTypes.bool,
    isEvent: PropTypes.bool,
    label: PropTypes.string,
    name: PropTypes.string,
    priceMin: PropTypes.number,
    priceMax: PropTypes.number,
    thumbUrl: PropTypes.string,
  }),
  _geoloc: PropTypes.shape({
    lat: PropTypes.number,
    lng: PropTypes.number,
  }),
  venue: PropTypes.shape({
    departmentCode: PropTypes.string,
    name: PropTypes.string,
    publicName: PropTypes.string,
  }),
  objectID: PropTypes.string.isRequired,
}

ResultsList.defaultProps = {
  search: '',
}

ResultsList.propTypes = {
  currentPage: PropTypes.number.isRequired,
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }).isRequired,
  isLoading: PropTypes.bool.isRequired,
  loadMore: PropTypes.func.isRequired,
  results: PropTypes.arrayOf(PropTypes.shape(SearchHit)).isRequired,
  resultsCount: PropTypes.number.isRequired,
  search: PropTypes.string,
  totalPagesNumber: PropTypes.number.isRequired,
}
