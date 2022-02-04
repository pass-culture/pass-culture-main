import invert from 'lodash.invert'
import uniq from 'lodash.uniq'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { withRouter } from 'react-router-dom'

import { stringify } from 'utils/query-string'

import { getObjectWithMappedKeys } from './getObjectWithMappedKeys'
import { selectQueryParamsFromQueryString } from './selectQueryParamsFromQueryString'

export const withQueryRouter =
  (config = {}) =>
  WrappedComponent => {
    const { mapper, translater } = config
    const creationKey = config.creationKey || 'creation'
    const modificationKey = config.modificationKey || 'modification'

    let invertedMapper
    if (mapper) {
      invertedMapper = invert(mapper)
    }

    class _withQueryRouter extends PureComponent {
      constructor(props) {
        super(props)
        this.query = {
          add: this.add,
          change: this.change,
          changeToCreation: this.changeToCreation,
          changeToModification: this.changeToModification,
          changeToReadOnly: this.changeToReadOnly,
          clear: this.clear,
          context: this.context,
          parse: this.parse,
          remove: this.remove,
          translate: this.translate,
        }
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
          /* eslint-disable no-console */
          console.warn(
            `Weird did you forget to mention this ${key} query param in your withQueryRouter hoc?`
          )
        }

        this.change({ [key]: nextValue })
      }

      clear = () => {
        const { history, location } = this.props
        history.push(location.pathname)
      }

      change = (notTranslatedQueryParamsUpdater, changeConfig = {}) => {
        const { history, location } = this.props
        const queryParams = this.parse()

        const historyMethod = changeConfig.historyMethod || 'push'
        const pathname = changeConfig.pathname || location.pathname

        let queryParamsUpdater = notTranslatedQueryParamsUpdater
        if (translater) {
          queryParamsUpdater = translater(queryParamsUpdater)
        } else if (mapper) {
          queryParamsUpdater = getObjectWithMappedKeys(
            queryParamsUpdater,
            invertedMapper
          )
        }

        const queryParamsUpdaterKeys = Object.keys(queryParamsUpdater)
        const concatenatedQueryParamKeys = Object.keys(queryParams).concat(
          queryParamsUpdaterKeys
        )
        const queryParamsKeys = uniq(concatenatedQueryParamKeys)

        const nextQueryParams = {}
        queryParamsKeys.forEach(queryParamsKey => {
          if (queryParamsUpdater[queryParamsKey]) {
            nextQueryParams[queryParamsKey] = queryParamsUpdater[queryParamsKey]
            return
          }
          if (
            queryParamsUpdater[queryParamsKey] !== null &&
            typeof queryParams[queryParamsKey] !== 'undefined'
          ) {
            nextQueryParams[queryParamsKey] = queryParams[queryParamsKey]
            return
          }
          if (queryParamsUpdater[queryParamsKey] === '') {
            nextQueryParams[queryParamsKey] = null
          }
        })

        const nextLocationSearch = stringify(nextQueryParams)
        const changedPath = `${pathname}?${nextLocationSearch}`

        history[historyMethod](changedPath)
      }

      context = (config = {}) => {
        const { key } = config
        if (key) {
          return this.contextWithEntityInSearch(config)
        }
        return this.contextWithEntityInPathname(config)
      }

      contextWithEntityInPathname = (config = {}) => {
        const {
          location: { pathname },
        } = this.props
        const queryParams = this.parse()

        const re = new RegExp(`(${creationKey})$`)
        const matchedResults = pathname.match(re)
        const matchedKey = matchedResults && matchedResults[0]
        if (matchedKey) {
          return this.creationContextWithEntityInPathname(config)
        }

        if (Object.keys(queryParams).includes(modificationKey)) {
          return this.modificationContextWithEntityInPathname(config)
        }

        return this.readOnlyContextWithEntityInPathname()
      }

      creationContextWithEntityInPathname = (config = {}) => {
        const { id } = config
        if (id) {
          if (id === creationKey) {
            return {
              isCreatedEntity: true,
              isModifiedEntity: false,
              method: 'POST',
              readOnly: false,
            }
          }
          return {
            isCreatedEntity: false,
            isModifiedEntity: false,
            readOnly: true,
          }
        }
        return {
          isCreatedEntity: true,
          isModifiedEntity: false,

          method: 'POST',
          readOnly: false,
        }
      }

      modificationContextWithEntityInPathname = (config = {}) => {
        const { id } = config
        const {
          location: { pathname },
        } = this.props
        if (id) {
          if (pathname.endsWith(id)) {
            return {
              isCreatedEntity: false,
              isModifiedEntity: true,
              method: 'PATCH',
              readOnly: false,
            }
          }
          return {
            isCreatedEntity: false,
            isModifiedEntity: false,
            readOnly: true,
          }
        }

        return {
          isCreatedEntity: false,
          isModifiedEntity: true,
          method: 'PATCH',
          readOnly: false,
        }
      }

      readOnlyContextWithEntityInPathname = () => {
        return {
          isCreatedEntity: false,
          isModifiedEntity: false,
          method: null,
          readOnly: true,
        }
      }

      contextWithEntityInSearch = (config = {}) => {
        const { id, key } = config
        const queryParams = this.parse()
        let paramKey = key
        let paramValue = queryParams[paramKey]

        const isCreationSearch =
          paramValue === creationKey ||
          (creationKey.test && creationKey.test(paramValue))
        if (!id && isCreationSearch) {
          return this.creationContextWithEntityInSearch(config)
        }

        if (!paramValue) {
          paramKey = `${key}${id}`
          paramValue = queryParams[paramKey]
        }
        if (paramValue === modificationKey) {
          return this.modificationContextWithEntityInSearch(config)
        }

        return this.readOnlyContextWithEntityInSearch(config)
      }

      creationContextWithEntityInSearch = (config = {}) => {
        const { key } = config
        return {
          isCreatedEntity: true,
          isModifiedEntity: false,
          key,
          method: 'POST',
          readOnly: false,
        }
      }

      modificationContextWithEntityInSearch = (config = {}) => {
        const { key } = config
        return {
          isCreatedEntity: false,
          isModifiedEntity: true,
          key,
          method: 'PATCH',
          readOnly: false,
        }
      }

      readOnlyContextWithEntityInSearch = (config = {}) => {
        const { key } = config
        return {
          isCreatedEntity: false,
          isModifiedEntity: false,
          key,
          method: null,
          readOnly: true,
        }
      }

      changeToCreation = (queryParamsUpdater, contextConfig = {}) => {
        const { key } = contextConfig
        const { location } = this.props
        const { pathname } = location

        const creationChange = Object.assign({}, queryParamsUpdater)
        if (!key) {
          const creationPathname = `${pathname}/${creationKey}`
          this.change(creationChange, { pathname: creationPathname })
          return
        }

        creationChange[key] = creationKey

        this.change(creationChange)
      }

      changeToModification = (queryParamsUpdater, contextConfig = {}) => {
        const { id, key } = contextConfig
        const { location } = this.props
        const { pathname } = location

        const modificationChange = Object.assign({}, queryParamsUpdater)

        if (!key) {
          modificationChange[modificationKey] = ''
          if (id) {
            const modifiedPathname = `${pathname}/${id}`
            this.change(modificationChange, { pathname: modifiedPathname })
            return
          }
          this.change(modificationChange)
          return
        }

        const queryParams = this.parse()
        Object.keys(queryParams).forEach(queryKey => {
          if (queryKey.startsWith(key)) {
            modificationChange[queryKey] = null
          }
        })
        const nextQueryKey = `${key}${id}`
        modificationChange[nextQueryKey] = modificationKey

        this.change(modificationChange)
      }

      changeToReadOnly = (queryParamsUpdater, contextConfig = {}) => {
        const { id, key } = contextConfig
        const { location } = this.props
        const { pathname } = location
        const queryParams = this.parse()

        const readOnlyChange = Object.assign({}, queryParamsUpdater)
        if (!key) {
          if (pathname.endsWith(creationKey)) {
            let readOnlyPathname = pathname.slice(0, -creationKey.length - 1)
            if (id) {
              readOnlyPathname = `${readOnlyPathname}/${id}`
            }

            this.change(readOnlyChange, { pathname: readOnlyPathname })
            return
          }

          if (typeof queryParams[modificationKey] !== 'undefined') {
            readOnlyChange[modificationKey] = null
            if (id) {
              const readOnlyPathname = pathname.slice(0, -id.length - 1)
              this.change(readOnlyChange, { pathname: readOnlyPathname })
              return
            }
            this.change(readOnlyChange)
            return
          }

          console.warn(
            'tried to changeToReadOnly but did not find a pathname context'
          )
          return
        }

        Object.keys(queryParams).forEach(queryKey => {
          if (queryKey.startsWith(key)) {
            readOnlyChange[queryKey] = null
          }
        })

        this.change(readOnlyChange)
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

      translate = () => {
        const queryParams = this.parse()
        if (translater) {
          return translater(queryParams)
        }
        if (mapper) {
          return getObjectWithMappedKeys(queryParams, mapper)
        }
        return queryParams
      }

      render() {
        return <WrappedComponent {...this.props} query={this.query} />
      }
    }

    _withQueryRouter.propTypes = {
      history: PropTypes.shape().isRequired,
      location: PropTypes.shape().isRequired,
    }

    _withQueryRouter.WrappedComponent = WrappedComponent

    return withRouter(_withQueryRouter)
  }

export default withQueryRouter
