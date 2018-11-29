import get from 'lodash.get'
import uniq from 'lodash.uniq'
import PropTypes from 'prop-types'
import { parse, stringify } from 'query-string'
import React, { PureComponent } from 'react'
import { withRouter } from 'react-router-dom'

const query = {
  params: {},
}

export const withQueryRouter = WrappedComponent => {
  class _withQueryRouter extends PureComponent {
    constructor() {
      super()

      const queryMethods = {
        add: this.add,
        change: this.change,
        orderBy: this.orderBy,
        remove: this.remove,
        reverseOrder: this.reverseOrder,
      }

      Object.assign(query, queryMethods)

      this.state = {
        canRenderWhenPageIsInitialized: false,
      }
    }

    static getDerivedStateFromProps(nextProps) {
      const { location } = nextProps

      query.params = parse(location.search)

      return {
        canRenderWhenPageIsInitialized: true,
      }
    }

    clear = () => {
      const { history, location } = this.props
      history.push(location.pathname)
    }

    reverseOrder = () => {
      const {
        params: { orderBy },
      } = query
      if (!orderBy) {
        console.warn('there is no orderBy in the query')
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
      const {
        params: { orderBy },
      } = query
      if (!orderBy) {
        console.warn('there is no orderBy in the query')
        return
      }
      const [, orderDirection] = orderBy.split('+')
      this.change({
        orderBy: [e.target.value, orderDirection].join('+'),
      })
    }

    change = (queryParamsUpdater, changeConfig = {}) => {
      const { history, location } = this.props
      const historyMethod = changeConfig.historyMethod || 'push'
      const pathname = changeConfig.pathname || location.pathname

      const queryParamsKeys = uniq(
        Object.keys(query.params).concat(Object.keys(queryParamsUpdater))
      )

      const nextQueryParams = {}
      queryParamsKeys.forEach(queryParamsKey => {
        if (queryParamsUpdater[queryParamsKey]) {
          nextQueryParams[queryParamsKey] = queryParamsUpdater[queryParamsKey]
          return
        }
        if (
          queryParamsUpdater[queryParamsKey] !== null &&
          query.params[queryParamsKey]
        ) {
          nextQueryParams[queryParamsKey] = query.params[queryParamsKey]
        }
      })

      const nextLocationSearch = stringify(nextQueryParams)

      const newPath = `${pathname}?${nextLocationSearch}`

      history[historyMethod](newPath)
    }

    add = (key, value) => {
      const { params } = query

      let nextValue = value
      const previousValue = params[key]
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
      const { params } = query

      const previousValue = params[key]
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
      return <WrappedComponent {...this.props} query={query} />
    }
  }

  _withQueryRouter.propTypes = {
    history: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
  }

  _withQueryRouter.WrappedComponent = WrappedComponent

  return withRouter(_withQueryRouter)
}

export default withQueryRouter
