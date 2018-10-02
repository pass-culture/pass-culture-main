import React from 'react'
import { InfiniteScroller } from 'pass-culture-shared'
import PropTypes from 'prop-types'

import SearchResultItem from './SearchResultItem'
import NavResultsHeader from './NavResultsHeader'
import { searchResultsTitle } from './utils'

const SearchResults = ({ items, keywords, loadMoreHandler, pagination }) => {
  const resultTitle = searchResultsTitle(
    keywords,
    items,
    pagination.windowQuery
  )
  // TODO FixMe with data from api & selector
  const typeSublabels = [
    {
      description:
        'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
      sublabel: 'Applaudir',
    },
  ]
  return (
    <div className="search-results">
      <h2
        className="fs15 is-uppercase is-italic is-semi-bold mb12"
        id="results-title"
      >
        {resultTitle}
      </h2>
      <NavResultsHeader
        searchType={pagination.windowQuery.categories}
        typeSublabels={typeSublabels[0]}
      />
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
}

export default SearchResults
