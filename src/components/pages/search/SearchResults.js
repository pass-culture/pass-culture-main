import React from 'react'
import PropTypes from 'prop-types'
import { InfiniteScroller, pluralize } from 'pass-culture-shared'

import SearchResultItem from './SearchResultItem'

const SearchResults = ({ items, keywords, loadMoreHandler, queryParams }) => {
  // console.log('items', items);
  // console.log('keywords', keywords);
  // console.log('queryParams', queryParams);
  // console.log('loadMoreHandler', loadMoreHandler);
  const count = items.length
  const resultString = pluralize(count, 'résultats')
  const keywordsString = decodeURI(keywords || '')
  const typesString = decodeURI(queryParams.types || '')
  const resultTitle = `${keywordsString} ${typesString}: ${resultString}`
  // console.log('resultTitle', resultTitle);
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
