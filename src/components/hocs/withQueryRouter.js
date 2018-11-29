import get from 'lodash.get'
import uniq from 'lodash.uniq'
import PropTypes from 'prop-types'
import { parse, stringify } from 'query-string'
import React, { PureComponent } from 'react'
import { withRouter } from 'react-router-dom'

const pagination = {
  query: {},
}

export const withQueryRouter = WrappedComponent => {
  class _withQueryRouter extends PureComponent {
    constructor() {
      super()

      const paginationMethods = {
        add: this.add,
        change: this.change,
        orderBy: this.orderBy,
        remove: this.remove,
        reverseOrder: this.reverseOrder,
      }

      Object.assign(pagination, paginationMethods)

      this.state = {
        canRenderWhenPageIsInitialized: false,
      }
    }

    static getDerivedStateFromProps(nextProps) {
      const { location } = nextProps

      pagination.query = parse(location.search)

      return {
        canRenderWhenPageIsInitialized: true,
      }
    }

    clear = () => {
      const { history, location } = this.props
      history.push(location.pathname)
    }

    reverseOrder = () => {
      const { query } = this.state
      const { orderBy } = query || {}
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
      const { query } = this.state
      const { orderBy } = query || {}
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
      const query = parse(location.search)
      const historyMethod = changeConfig.historyMethod || 'push'
      const pathname = changeConfig.pathname || location.pathname

      const queryKeys = uniq(
        Object.keys(query).concat(Object.keys(queryUpdater))
      )

      const nextQuery = {}
      queryKeys.forEach(queryKey => {
        if (queryUpdater[queryKey]) {
          nextQuery[queryKey] = queryUpdater[queryKey]
          return
        }
        if (queryUpdater[queryKey] !== null && query[queryKey]) {
          nextQuery[queryKey] = query[queryKey]
        }
      })

      const nextLocationSearch = stringify(nextQuery)

      const newPath = `${pathname}?${nextLocationSearch}`

      history[historyMethod](newPath)
    }

    add = (key, value) => {
      const { query } = this.state

      let nextValue = value
      const previousValue = query[key]
      if (get(previousValue, 'length')) {
        const args = previousValue.split(',').concat([value])
        args.sort()
        nextValue = args.join(',')
      } else if (typeof previousValue === 'undefined') {
        console.warn(
          `Weird did you forget to mention this ${key} query param in your withQueryRouter hoc ?`
        )
      }

      this.change({ [key]: nextValue })
    }

    remove = (key, value) => {
      const { query } = this.state

      const previousValue = query[key]
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
          `Weird did you forget to mention this ${key} query param in your withQueryRouter hoc ?`
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

  _withQueryRouter.propTypes = {
    history: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
  }

  return withRouter(_withQueryRouter)
}

export default withQueryRouter
