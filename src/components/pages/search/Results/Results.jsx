import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import InfiniteScroll from 'react-infinite-scroller'

import RecommendationItemContainer from './RecommendationItem/RecommendationItemContainer'
import { getVisibleParamsAreEmpty, searchResultsTitle } from '../helpers'
import Spinner from '../../../layout/Spinner'

class Results extends PureComponent {
  constructor() {
    super()
    this.state = {
      hasReceivedFirstSuccessData: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const { history, query } = this.props
    const queryParams = query.parse()
    const queryParamsAreEmpty = getVisibleParamsAreEmpty(queryParams)
    const queryParamsAndKeywordsAreEmpty = queryParamsAreEmpty && !queryParams['mots-cles']
    if (queryParamsAndKeywordsAreEmpty) {
      history.replace('/recherche/resultats')
    }
  }

  componentDidUpdate(prevProps) {
    const { items } = this.props

    const itemsHaveReceivedNextData = items.length > prevProps.items.length
    if (itemsHaveReceivedNextData) {
      this.handleShouldCancelLoading()
      const previousItemsWasEmpty = prevProps.items.length === 0
      if (previousItemsWasEmpty) {
        this.handleSetHasReceivedFirstSuccessData()
      }
      return
    }

    if (items !== prevProps.items) {
      this.handleSetHasReceivedFirstSuccessData()
    }
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
    const { cameFromOfferTypesPage, hasMore, items, keywords, query } = this.props
    const { hasReceivedFirstSuccessData, isLoading } = this.state
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
            className={classnames('fs15 is-uppercase is-italic is-semi-bold mb12', {
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
            pageStart={parseInt(queryParams.page || 1, 10)}
            threshold={threshold}
            useWindow={false}
          >
            {items.map(item => (
              <RecommendationItemContainer
                key={queryParams.page + item.id}
                recommendation={item}
              />
            ))}
          </InfiniteScroll>
        )}
      </div>
    )
  }
}

Results.defaultProps = {
  hasMore: false,
  items: [],
  keywords: '',
}

Results.propTypes = {
  cameFromOfferTypesPage: PropTypes.bool.isRequired,
  hasMore: PropTypes.bool,
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
  }).isRequired,
  items: PropTypes.arrayOf(PropTypes.shape()),
  keywords: PropTypes.string,
  query: PropTypes.shape().isRequired,
}

export default Results
