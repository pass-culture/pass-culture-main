/* eslint-disable */
import classnames from 'classnames'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { shallowCompare } from 'react-redux'

import FilterByDates from './FilterByDates'
import FilterByDistance from './FilterByDistance'
import FilterByOfferTypes from './FilterByOfferTypes'

import { getFirstChangingKey, INITIAL_FILTER_PARAMS } from '../search/utils'

class SearchFilter extends Component {
  constructor(props) {
    super(props)
    this.state = {
      add: this.handleQueryAdd,
      change: this.handleQueryChange,
      remove: this.handleQueryRemove,

      query: Object.assign({}, props.pagination.windowQuery),
      isNew: false,
    }
  }

  componentDidUpdate(prevProps) {
    const { pagination } = this.props
    const { windowQuery } = pagination
    // TODO: eslint does not support setState inside componentDidUpdate
    if (windowQuery !== prevProps.pagination.windowQuery) {
      this.setState({
        query: windowQuery,
        isNew: false,
      })
    }
  }

  onFilterClick = () => {
    const { pagination } = this.props
    const { isNew, query } = this.state

    pagination.change(query, {
      isClearingData: isNew,
      pathname: '/recherche/resultats',
    })
  }

  onResetClick = () => {
    const isNew = getFirstChangingKey(
      this.props.pagination.windowQuery,
      INITIAL_FILTER_PARAMS
    )

    this.setState({
      isNew,
      query: INITIAL_FILTER_PARAMS,
    })
  }

  handleQueryChange = (newValue, callback) => {
    const { pagination } = this.props
    const { query } = this.state

    const nextFilterParams = Object.assign({}, query, newValue)
    const isNew = getFirstChangingKey(pagination.windowQuery, newValue)

    this.setState(
      {
        query: nextFilterParams,
        isNew,
      },
      callback
    )
  }

  handleQueryAdd = (key, value, callback) => {
    const { query } = this.state
    const encodedValue = encodeURI(value)
    let nextValue = encodedValue
    const previousValue = query[key]
    if (get(previousValue, 'length')) {
      const args = previousValue.split(',').concat([encodedValue])
      args.sort()
      nextValue = args.join(',')
    }

    this.handleQueryChange({ [key]: nextValue }, callback)
  }

  handleQueryRemove = (key, value, callback) => {
    const { query } = this.state

    const previousValue = query[key]

    if (get(previousValue, 'length')) {
      const encodedValue = encodeURI(value)
      let nextValue = previousValue
        .replace(`,${encodedValue}`, '')
        .replace(encodedValue, '')
      if (nextValue[0] === ',') {
        nextValue = nextValue.slice(1)
      }
      this.handleQueryChange({ [key]: nextValue }, callback)
    }
  }

  render() {
    return (
      <div
        className={classnames({ 'is-invisible': !this.props.isVisible })}
        id="search-filter-menu">
        <FilterByDates filter={this.state} title="QUAND" />
        <FilterByDistance filter={this.state} title="OÙ" />
        <FilterByOfferTypes filter={this.state} title="QUOI" />
        <button
          className="button fs24"
          onClick={this.onResetClick}
          type="button">
          Réinitialiser
        </button>
        <button
          className="button fs24"
          onClick={this.onFilterClick}
          type="button">
          Filtrer
        </button>
      </div>
    )
  }
}

SearchFilter.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  pagination: PropTypes.object.isRequired,
}

export default SearchFilter
