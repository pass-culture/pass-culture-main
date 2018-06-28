import React, { Component } from 'react'
import classnames from 'classnames'

const UP = 'up'
const DOWN = 'down'

class InfiniteScroller extends Component {

  constructor(props) {
    super(props);
    this.state = {
      errors: null,
      isLoading: false,
      isFinished: false,
      lastScrollTop: 0,
      loadCounts: 1, // First one is at page level
    }
  }

  static defaultProps = {
    Tag: 'ul',
    loadScrollRatio: 0.9,
    scrollingElement: document.documentElement,
    loadingInfo: <li>Chargement ...</li>
  }

  scrollWatch = e => {
    const {
      isLoading,
      isFinished,
      loadCounts,
    } = this.state
    const {
      loadScrollRatio,
      scrollingElement
    } = this.props

    const {
      scrollTop,
      scrollHeight,
      clientHeight,
    } = scrollingElement

    const pageScrollRatio = scrollTop / (scrollHeight - clientHeight)
    const scrollDirection = this.state.lastScrollTop > scrollTop ? UP : DOWN
    const shouldLoadMore = !isFinished && !isLoading && scrollDirection === DOWN && pageScrollRatio > loadScrollRatio

    console.log('scrolling', pageScrollRatio, scrollDirection)

    this.setState({
      isLoading: shouldLoadMore,
      lastScrollTop: scrollTop,
      loadCounts: loadCounts + (shouldLoadMore ? 1 : 0),
    })
    shouldLoadMore && this.props.handleLoadMore(this.loadSuccess, this.loadError, loadCounts)
  }

  loadSuccess = (state, action) => {
    console.log(state, action)
    this.setState({
      isLoading: false,
      isFinished: action.data.length === 0,
    })
  }

  loadError = (state, action) => {
    console.log(state, action)
    this.setState({
      isLoading: false,
      errors: action.errors,
    })
  }

  componentDidMount() {
    window.addEventListener('scroll', this.scrollWatch)
    this.setState({
      lastScrollTop: this.props.scrollingElement.scrollTop,
    })
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.scrollWatch)
  }

  render() {
    const {
      children,
      className,
      loadingInfo,
      Tag,
    } = this.props
    const {
      isLoading
    } = this.state
    return (
      <Tag className={classnames('infinite-scroller', className)}>
        {children}
        { isLoading && loadingInfo }
      </Tag>
    )
  }

}

export default InfiniteScroller