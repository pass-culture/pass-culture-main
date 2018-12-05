import uniq from 'lodash.uniq'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { PureComponent } from 'react'
import { withRouter } from 'react-router-dom'

import { selectQueryParamsFromQueryString } from '../../helpers/selectQueryParamsFromQueryString'

export const withQueryRouter = WrappedComponent => {
  class _withQueryRouter extends PureComponent {
    constructor(props) {
      super(props)
      this.query = {
        add: this.add,
        change: this.change,
        clear: this.clear,
        parse: this.parse,
        remove: this.remove,
      }
    }

    clear = () => {
      const { history, location } = this.props
      history.push(location.pathname)
    }

    change = (queryParamsUpdater, changeConfig = {}) => {
      const { history, location } = this.props
      const queryParams = this.parse()

      const historyMethod = changeConfig.historyMethod || 'push'
      const pathname = changeConfig.pathname || location.pathname
      const queryParamsKeys = uniq(
        Object.keys(queryParams).concat(Object.keys(queryParamsUpdater))
      )

      const nextQueryParams = {}
      queryParamsKeys.forEach(queryParamsKey => {
        if (queryParamsUpdater[queryParamsKey]) {
          nextQueryParams[queryParamsKey] = queryParamsUpdater[queryParamsKey]
          return
        }
        if (
          queryParamsUpdater[queryParamsKey] !== null &&
          queryParams[queryParamsKey]
        ) {
          nextQueryParams[queryParamsKey] = queryParams[queryParamsKey]
        }
      })

      const nextLocationSearch = stringify(nextQueryParams)

      const newPath = `${pathname}?${nextLocationSearch}`

      history[historyMethod](newPath)
    }

    add = (key, value) => {
      const queryParams = this.parse()

      let nextValue = value
      const previousValue = queryParams[key]
      if (previousValue && previousValue.length) {
        const args = previousValue.split(',').concat([value])
        args.sort()
        nextValue = args.join(',')
      } else if (typeof previousValue === 'undefined') {
        console.warn(
          `Weird did you forget to mention this ${key} query param in your withQueryRouter hoc?`
        )
      }

      this.change({ [key]: nextValue })
    }

    parse = () => {
      const { location } = this.props
      return selectQueryParamsFromQueryString(location.search)
    }

    remove = (key, value) => {
      const queryParams = this.parse()

      const previousValue = queryParams[key]
      if (previousValue && previousValue.length) {
        let nextValue = previousValue
          .replace(`,${value}`, '')
          .replace(value, '')
        if (nextValue[0] === ',') {
          nextValue = nextValue.slice(1)
        }
        this.change({ [key]: nextValue })
      } else if (typeof previousValue === 'undefined') {
        console.warn(
          `Weird did you forget to mention this ${key} query param in your withQueryRouter hoc?`
        )
      }
    }

    render() {
      return <WrappedComponent {...this.props} query={this.query} />
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
