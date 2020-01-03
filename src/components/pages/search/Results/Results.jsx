import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import InfiniteScroll from 'react-infinite-scroller'
import Spinner from '../../../layout/Spinner/Spinner'

import Teaser from '../../../layout/Teaser/TeaserContainer'
import { searchResultsTitle } from '../helpers'

const ITEMS_PER_PAGE = 10

class Results extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      hasMore: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const { items } = this.props
    if (items.length) {
      this.handleSetHasMore(items.length)
    }
  }

  componentDidUpdate(prevProps) {
    const { items } = this.props

    const itemsHaveReceivedNextData = items.length > prevProps.items.length
    if (itemsHaveReceivedNextData) {
      const newBatchOfItemsLength = items.length - prevProps.items.length
      this.handleSetHasMore(newBatchOfItemsLength)
      this.handleShouldCancelLoading()
      return
    }

    if (items !== prevProps.items) {
      const newBatchOfItemsLength = items.length - prevProps.items.length
      this.handleSetHasMore(newBatchOfItemsLength)
    }
  }

  handleSetHasMore = newBatchOfItemsLength => {
    const hasMore = newBatchOfItemsLength === ITEMS_PER_PAGE
    this.setState({ hasMore })
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
    if (isLoading) return

    this.setState({ isLoading: true }, () => {
      query.change({ page }, { historyMethod: 'replace' })
    })
  }

  getScrollParent = () => document.querySelector('.page-content')

  render() {
    const { cameFromOfferTypesPage, items, keywords, query } = this.props
    const { hasMore, hasReceivedFirstSuccessData, isLoading } = this.state
    const queryParams = query.parse()
    const resultTitle = searchResultsTitle(
      keywords,
      items,
      cameFromOfferTypesPage,
      hasReceivedFirstSuccessData
    )

    const reachableThresholdThatTriggersLoadMore = -10
    const unreachableThreshold = -1000
    const threshold = isLoading ? unreachableThreshold : reachableThresholdThatTriggersLoadMore

    return (
      <div className="search-results">
        {resultTitle && (
          <h2
            className={`search-results-title ${cameFromOfferTypesPage ? 'nav-result-title' : ''}`}
            id="results-title"
          >
            {resultTitle}
          </h2>
        )}
        {items && items.length > 0 && (
          <InfiniteScroll
            element="ul"
            getScrollParent={this.getScrollParent}
            hasMore={hasMore}
            loader={<Spinner key="loader" />}
            loadMore={this.loadMore}
            pageStart={parseInt(queryParams.page || 1, ITEMS_PER_PAGE)}
            threshold={threshold}
            useWindow={false}
          >
            {items.map(item => (
              <Teaser
                item={item}
                key={item.id}
              />
            ))}
          </InfiniteScroll>
        )}
      </div>
    )
  }
}

Results.defaultProps = {
  items: [],
  keywords: '',
}

Results.propTypes = {
  cameFromOfferTypesPage: PropTypes.bool.isRequired,
  items: PropTypes.arrayOf(PropTypes.shape()),
  keywords: PropTypes.string,
  query: PropTypes.shape().isRequired,
}

export default Results
