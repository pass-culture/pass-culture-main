import classnames from 'classnames'
import React, { PureComponent } from 'react'
import InfiniteScroll from 'react-infinite-scroller'
import PropTypes from 'prop-types'

import SearchResultItem from './SearchResultItem'
import { searchResultsTitle } from './utils'
import { withQueryRouter } from '../../hocs/withQueryRouter'
import Spinner from '../../layout/Spinner'

class SearchResults extends PureComponent {
  constructor() {
    super()
    this.state = {
      isLoading: false,
    }
  }

  componentDidUpdate(prevProps) {
    const { items } = this.props
    if (items !== prevProps.items) {
      this.handleShouldCancelLoading()
    }
  }

  handleShouldCancelLoading = () => {
    const { isLoading } = this.state
    if (isLoading) {
      this.setState({ isLoading: false })
    }
  }

  loadMore = page => {
    const { query } = this.props
    const { isLoading } = this.state
    if (isLoading) {
      return
    }

    this.setState({ isLoading: true }, () => query.change({ page }))
  }

  render() {
    const {
      cameFromOfferTypesPage,
      items,
      hasMore,
      keywords,
      query,
    } = this.props
    const queryParams = query.parse()
    const resultTitle = searchResultsTitle(
      keywords,
      items,
      queryParams,
      cameFromOfferTypesPage
    )
    const { isLoading } = this.state

    const reachableThresholdThatTriggersLoadMore = -10
    const unreachableThreshold = -1000
    const threshold = isLoading
      ? unreachableThreshold
      : reachableThresholdThatTriggersLoadMore

    return (
      <div className="search-results">
        <h2
          className={classnames(
            'fs15 is-uppercase is-italic is-semi-bold mb12',
            {
              [`nav-result-title`]: cameFromOfferTypesPage,
            }
          )}
          id="results-title"
        >
          {resultTitle}
        </h2>
        {items && items.length > 0 && (
          <InfiniteScroll
            element="ul"
            getScrollParent={() => document.querySelector('.page-content')}
            hasMore={hasMore}
            loadMore={this.loadMore}
            loader={<Spinner key="loader" />}
            pageStart={parseInt(queryParams.page || 1, 10)}
            threshold={threshold}
            useWindow={false}
          >
            {items.map(item => (
              <SearchResultItem key={item.id} recommendation={item} />
            ))}
          </InfiniteScroll>
        )}
      </div>
    )
  }
}

SearchResults.defaultProps = {
  hasMore: false,
  items: [],
  keywords: '',
}

SearchResults.propTypes = {
  cameFromOfferTypesPage: PropTypes.bool.isRequired,
  hasMore: PropTypes.bool,
  items: PropTypes.array,
  keywords: PropTypes.string,
  query: PropTypes.object.isRequired,
}

export default withQueryRouter(SearchResults)
