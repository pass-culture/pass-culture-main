import classnames from 'classnames'
import React from 'react'
import { InfiniteScroller } from 'pass-culture-shared'
import PropTypes from 'prop-types'

import SearchResultItem from './SearchResultItem'
import { searchResultsTitle } from './utils'

const SearchResults = ({
  items,
  keywords,
  loadMoreHandler,
  pagination,
  withNavigation,
}) => {
  const resultTitle = searchResultsTitle(
    keywords,
    items,
    pagination.windowQuery,
    withNavigation
  )

  return (
    <div className="search-results">
      <h2
        className={classnames('fs15 is-uppercase is-italic is-semi-bold mb12', {
          [`nav-result-title`]: withNavigation,
        })}
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
}

SearchResults.propTypes = {
  items: PropTypes.array,
  keywords: PropTypes.string,
  loadMoreHandler: PropTypes.func.isRequired,
  pagination: PropTypes.object.isRequired,
  withNavigation: PropTypes.bool.isRequired,
}

export default SearchResults
