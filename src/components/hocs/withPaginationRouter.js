import get from 'lodash.get'
import uniq from 'lodash.uniq'
import PropTypes from 'prop-types'
import { parse, stringify } from 'query-string'
import React, { PureComponent } from 'react'
import { withRouter } from 'react-router-dom'

const pagination = {
  windowQuery: {},
}

export const withPaginationRouter = WrappedComponent => {
  class _withPaginationRouter extends PureComponent {
    constructor() {
      super()

      const paginationMethods = {
        add: this.add,
        change: this.change,
        orderBy: this.orderBy,
        remove: this.remove,
        reverseOrder: this.reverseOrder,
        setPage: this.setPage,
      }

      Object.assign(pagination, paginationMethods)

      this.state = {
        canRenderWhenPageIsInitialized: false,
      }
    }

    componentDidMount() {
      this.change({ page: null })
      this.setState({ canRenderWhenPageIsInitialized: true })
    }

    static getDerivedStateFromProps(nextProps) {
      const windowQuery = parse(nextProps.location.search)
      const windowQueryString = stringify(Object.assign({}, windowQuery))

      return {
        windowQuery,
        windowQueryString,
      }
    }

    clear = () => {
      const { history, location } = this.props
      this.setState({ windowQuery: {} })
      history.push(location.pathname)
    }

    reverseOrder = () => {
      const { windowQuery } = this.state
      const { orderBy } = windowQuery || {}
      if (!orderBy) {
        console.warn('there is no orderBy in the window query')
        return
      }
      const [orderName, orderDirection] = orderBy.split('+')
      this.change({
        orderBy: [orderName, orderDirection === 'desc' ? 'asc' : 'desc'].join(
          '+'
        ),
      })
    }

    orderBy = e => {
      const { windowQuery } = this.state
      const { orderBy } = windowQuery || {}
      if (!orderBy) {
        console.warn('there is no orderBy in the window query')
        return
      }
      const [, orderDirection] = orderBy.split('+')
      this.change({
        orderBy: [e.target.value, orderDirection].join('+'),
      })
    }

    change = (queryUpdater, changeConfig = {}) => {
      const { history, location } = this.props
      const { windowQuery } = this.state
      const historyMethod = changeConfig.historyMethod || 'push'
      const pathname = changeConfig.pathname || location.pathname

      const queryKeys = uniq(
        Object.keys(windowQuery).concat(Object.keys(queryUpdater))
      )

      if (!queryUpdater.page) {
        queryUpdater.page = null
      }

      console.log('queryUpdater', queryUpdater, 'windowQuery', windowQuery)

      const newWindowQuery = {}
      queryKeys.forEach(queryKey => {
        if (queryUpdater[queryKey]) {
          newWindowQuery[queryKey] = queryUpdater[queryKey]
          return
        }
        if (queryUpdater[queryKey] !== null && windowQuery[queryKey]) {
          newWindowQuery[queryKey] = windowQuery[queryKey]
        }
      })
      const nextLocationSearch = stringify(newWindowQuery)

      console.log('nextLocationSearch', nextLocationSearch)
      pagination.windowQuery = newWindowQuery

      const newPath = `${pathname}?${nextLocationSearch}`

      history[historyMethod](newPath)
    }

    add = (key, value) => {
      const { windowQuery } = this.state

      let nextValue = value
      const previousValue = windowQuery[key]
      if (get(previousValue, 'length')) {
        const args = previousValue.split(',').concat([value])
        args.sort()
        nextValue = args.join(',')
      } else if (typeof previousValue === 'undefined') {
        console.warn(
          `Weird did you forget to mention this ${key} query param in your withPaginationRouter hoc ?`
        )
      }

      this.change({ [key]: nextValue })
    }

    remove = (key, value) => {
      const { windowQuery } = this.state

      const previousValue = windowQuery[key]
      if (get(previousValue, 'length')) {
        let nextValue = previousValue
          .replace(`,${value}`, '')
          .replace(value, '')
        if (nextValue[0] === ',') {
          nextValue = nextValue.slice(1)
        }
        this.change({ [key]: nextValue })
      } else if (typeof previousValue === 'undefined') {
        console.warn(
          `Weird did you forget to mention this ${key} query param in your withPaginationRouter hoc ?`
        )
      }
    }

    render() {
      const { canRenderWhenPageIsInitialized } = this.state
      if (!canRenderWhenPageIsInitialized) {
        return null
      }
      return <WrappedComponent {...this.props} pagination={pagination} />
    }
  }

  _withPaginationRouter.propTypes = {
    history: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
  }

  return withRouter(_withPaginationRouter)
}

export default withPaginationRouter
