/* eslint-disable */
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Transition } from 'react-transition-group'

import FilterByDates from './FilterByDates'
import FilterByDistance from './FilterByDistance'
import FilterByOfferTypes from './FilterByOfferTypes'

import { getFirstChangingKey, INITIAL_FILTER_PARAMS } from './utils'

const filtersPanelHeight = 455
const transitionDelay = 0
const transitionDuration = 500

const defaultStyle = {
  marginTop: `-${filtersPanelHeight}px`,
  transition: `margin-top ${transitionDuration}ms ease`,
}

const transitionStyles = {
  exiting: { marginTop: `-${filtersPanelHeight}px` },
  exited: { marginTop: `-${filtersPanelHeight}px` },
  entering: { marginTop: 0 },
  entered: { marginTop: 0 },
}

class SearchFilter extends Component {
  // add, remove and change passed as props via this.state to filter components
  // ex <FilterByDates filter={this.state} title="QUAND" />
  constructor(props) {
    super(props)
    this.state = {
      add: this.handleQueryAdd,
      change: this.handleQueryChange,
      isNew: false,
      query: Object.assign({}, props.pagination.windowQuery),
      remove: this.handleQueryRemove,
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
    })

    this.props.pagination.change(INITIAL_FILTER_PARAMS, {
      pathname: '/recherche/resultats',
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
    const { isVisible } = this.props
    return (
      <div className="is-relative is-clipped">
        <Transition in={isVisible} timeout={transitionDelay}>
          {status => (
            <div
              id="search-filter-menu"
              className={`is-full-width transition-status-${status}`}
              style={{ ...defaultStyle, ...transitionStyles[status] }}>
              <FilterByDates filter={this.state} title="QUAND" />
              <FilterByDistance filter={this.state} title="OÙ" />
              <FilterByOfferTypes filter={this.state} title="QUOI" />
              <div
                id="search-filter-menu-footer-controls"
                className="flex-columns mt20">
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  onClick={this.onResetClick}
                  type="button">
                  Réinitialiser
                </button>
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  onClick={this.onFilterClick}
                  type="button">
                  <span className="is-bold">Filtrer</span>
                </button>
              </div>
            </div>
          )}
        </Transition>
      </div>
    )
  }
}

SearchFilter.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  pagination: PropTypes.object.isRequired,
}

export default SearchFilter
