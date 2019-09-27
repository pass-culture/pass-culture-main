import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import InfiniteScroll from 'react-infinite-scroller'

import Teaser from '../../../layout/Teaser/TeaserContainer'
import { searchResultsTitle } from '../helpers'
import Spinner from '../../../layout/Spinner/Spinner'

const ITEMS_PER_PAGE = 10

class Results extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      hasMore: false,
      hasReceivedFirstSuccessData: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const { items } = this.props

    if (items.length) {
      this.handleSetHasMore(items.length)
      this.handleSetHasReceivedFirstSuccessData()
    }
  }

  componentDidUpdate(prevProps) {
    const { items } = this.props

    const itemsHaveReceivedNextData = items.length > prevProps.items.length
    if (itemsHaveReceivedNextData) {
      const newBatchOfItemsLength = items.length - prevProps.items.length
      this.handleSetHasMore(newBatchOfItemsLength)
      this.handleShouldCancelLoading()
      const previousItemsWasEmpty = prevProps.items.length === 0
      if (previousItemsWasEmpty) {
        this.handleSetHasReceivedFirstSuccessData()
      }
      return
    }

    if (items !== prevProps.items) {
      this.handleSetHasReceivedFirstSuccessData()
      const newBatchOfItemsLength = items.length - prevProps.items.length
      this.handleSetHasMore(newBatchOfItemsLength)
    }
  }

  handleSetHasMore = newBatchOfItemsLength => {
    const hasMore = newBatchOfItemsLength === ITEMS_PER_PAGE
    this.setState({ hasMore })
  }

  handleSetHasReceivedFirstSuccessData = () => {
    const { hasReceivedFirstSuccessData } = this.state

    if (!hasReceivedFirstSuccessData) {
      this.setState({ hasReceivedFirstSuccessData: true })
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
            className={classnames('search-results-title', {
              [`nav-result-title`]: cameFromOfferTypesPage,
            })}
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
            loadMore={this.loadMore}
            loader={<Spinner key="loader" />}
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
