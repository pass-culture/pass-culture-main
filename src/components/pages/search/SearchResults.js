import classnames from 'classnames'
import React, { PureComponent } from 'react'
import InfiniteScroll from 'react-infinite-scroller'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

import SearchResultItem from './SearchResultItem'
import { searchResultsTitle } from './utils'
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
    const { isLoading } = this.state
    if (isLoading && items !== prevProps.items) {
      /* eslint-disable react/no-did-update-set-state */
      this.setState({ isLoading: false })
    }
  }

  loadMore = page => {
    console.log('LOAD MORE', page)
    const { pagination } = this.props
    const { isLoading } = this.state
    if (isLoading) {
      return
    }

    this.setState({ isLoading: true }, () => pagination.change({ page }))
  }

  render() {
    const {
      items,
      hasMore,
      keywords,
      pagination: { windowQuery },
      withNavigation,
    } = this.props
    const resultTitle = searchResultsTitle(
      keywords,
      items,
      windowQuery,
      withNavigation
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
              [`nav-result-title`]: withNavigation,
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
            pageStart={parseInt(windowQuery.page || 1, 10)}
            threshold={threshold}
            useWindow={false}
          >
            {items.map(o => (
              <SearchResultItem key={o.id} recommendation={o} />
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
  hasMore: PropTypes.bool,
  items: PropTypes.array,
  keywords: PropTypes.string,
  pagination: PropTypes.object.isRequired,
  withNavigation: PropTypes.bool.isRequired,
}

export default withRouter(SearchResults)
