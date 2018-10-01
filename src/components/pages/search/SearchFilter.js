/* eslint-disable */
import classnames from 'classnames'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Transition } from 'react-transition-group'

import FilterByDates from './FilterByDates'
import FilterByDistance from './FilterByDistance'
import FilterByOfferTypes from './FilterByOfferTypes'

import { getFirstChangingKey, INITIAL_FILTER_PARAMS } from './utils'

const transitionDelay = 500
const transitionDuration = 250
const defaultStyle = {
  transitionDuration: `${transitionDuration}ms`,
  transitionProperty: 'top',
  transitionTimingFunction: 'ease',
}

const transitionStyles = {
  entered: { opacity: 1, top: 150 },
  // top:65
  entering: { opacity: 1, top: '-100%' },
  exited: { opacity: 0, top: '-100%' },
  exiting: { opacity: 0, top: '-100%' },
}

class SearchFilter extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isNew: false,
      query: Object.assign({}, props.pagination.windowQuery),
    }
  }

  componentDidUpdate(prevProps) {
    const { pagination } = this.props
    const { windowQuery } = pagination
    // TODO: eslint does not support setState inside componentDidUpdate
    if (windowQuery !== prevProps.pagination.windowQuery) {
      this.setState({
        isNew: false,
        query: windowQuery,
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
        isNew,
        query: nextFilterParams,
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
    const visible = this.props.filterIsVisible
    return (
      <Transition in={visible} timeout={transitionDelay}>
        {status => (
          <div
            // is-invisible is bulma style ?
            className={classnames({ 'is-invisible': !visible })}
            id="search-filter-menu"
            style={{ ...defaultStyle, ...transitionStyles[status] }}>
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
        )}
      </Transition>
    )
  }
}

SearchFilter.propTypes = {
  filterIsVisible: PropTypes.bool.isRequired,
  pagination: PropTypes.object.isRequired,
}

export default SearchFilter
