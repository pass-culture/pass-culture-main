import React from 'react'
import PropTypes from 'prop-types'
import { InfiniteScroller } from 'pass-culture-shared'

import SearchResultItem from './SearchResultItem'
import { searchResultsTitle } from './utils'

const SearchResults = ({ items, keywords, loadMoreHandler, queryParams }) => {
  const resultTitle = searchResultsTitle(keywords, items, queryParams)
  return (
    <div className="search-results">
      <h2
        className="fs15 is-uppercase is-italic is-semi-bold mb12"
        id="results-title"
      >
        {resultTitle}
      </h2>
      <InfiniteScroller handleLoadMore={loadMoreHandler}>
        {items &&
          items.map(o => <SearchResultItem key={o.id} recommendation={o} />)}
      </InfiniteScroller>
    </div>
  )
}

SearchResults.defaultProps = {
  items: [],
  keywords: '',
  queryParams: {},
}

SearchResults.propTypes = {
  items: PropTypes.array,
  keywords: PropTypes.string,
  loadMoreHandler: PropTypes.func.isRequired,
  queryParams: PropTypes.object,
}

export default SearchResults
