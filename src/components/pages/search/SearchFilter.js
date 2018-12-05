import get from 'lodash.get'
import { assignData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Transition } from 'react-transition-group'
import { compose } from 'redux'

import FilterByDates from './FilterByDates'
import FilterByDistance from './FilterByDistance'
import FilterByOfferTypes from './FilterByOfferTypes'
import { getFirstChangingKey, INITIAL_FILTER_PARAMS } from './utils'
import { withQueryRouter } from '../../hocs/withQueryRouter'

const filtersPanelHeight = 475
const transitionDelay = 0
const transitionDuration = 500

const defaultStyle = {
  marginTop: `-${filtersPanelHeight}px`,
  transition: `margin-top ${transitionDuration}ms ease`,
}

const transitionStyles = {
  entered: { marginTop: 0 },
  entering: { marginTop: 0 },
  exited: { marginTop: `-${filtersPanelHeight}px` },
  exiting: { marginTop: `-${filtersPanelHeight}px` },
}

class SearchFilter extends Component {
  constructor(props) {
    super(props)

    const { query } = props
    const queryParams = query.parse()

    this.state = {
      filterParamsMatchingQueryParams: false,
      params: Object.assign({}, queryParams),
    }
    this.filterActions = {
      add: this.handleQueryAdd,
      change: this.handleQueryChange,
      remove: this.handleQueryRemove,
      replace: this.handleQueryReplace,
    }
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props
    if (location.search !== prevProps.location.search) {
      this.handleReinitializeParams()
    }
  }

  handleReinitializeParams = () => {
    const { query } = this.props
    const queryParams = query.parse()

    this.setState({
      filterParamsMatchingQueryParams: false,
      params: queryParams,
    })
  }

  onFilterClick = () => {
    const { dispatch, onKeywordsEraseClick, query } = this.props
    const { filterParamsMatchingQueryParams, params } = this.state

    if (filterParamsMatchingQueryParams) {
      dispatch(assignData({ recommendations: [] }))
    }

    params.page = null

    if (onKeywordsEraseClick) {
      onKeywordsEraseClick()
    }

    query.change(params, { pathname: '/recherche/resultats' })
  }

  onResetClick = () => {
    const { dispatch, query } = this.props
    const queryParams = query.parse()

    dispatch(assignData({ recommendations: [] }))

    const filterParamsMatchingQueryParams = getFirstChangingKey(
      queryParams,
      INITIAL_FILTER_PARAMS
    )

    this.setState({ filterParamsMatchingQueryParams })

    query.change(INITIAL_FILTER_PARAMS, {
      pathname: '/recherche/resultats',
    })
  }

  handleQueryChange = (newValue, callback) => {
    const { query } = this.props
    const { params } = this.state
    const queryParams = query.parse()

    const nextFilterParams = Object.assign({}, params, newValue)
    const filterParamsMatchingQueryParams = getFirstChangingKey(
      queryParams,
      newValue
    )

    this.setState(
      {
        filterParamsMatchingQueryParams,
        params: nextFilterParams,
      },
      callback
    )
  }

  handleQueryAdd = (key, value, callback) => {
    const { params } = this.state
    const encodedValue = encodeURI(value)
    let nextValue = encodedValue
    const previousValue = params[key]
    if (get(previousValue, 'length')) {
      const args = previousValue.split(',').concat([encodedValue])
      args.sort()
      nextValue = args.join(',')
    }

    this.handleQueryChange({ [key]: nextValue }, callback)
  }

  handleQueryRemove = (key, value, callback) => {
    const { params } = this.state
    const previousValue = params[key]

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
              className={`is-full-width transition-status-${status} mb20`}
              style={{ ...defaultStyle, ...transitionStyles[status] }}
            >
              <FilterByDates
                filterActions={this.filterActions}
                filterState={this.state}
                title="QUAND"
              />
              <FilterByDistance
                filterActions={this.filterActions}
                filterState={this.state}
                title="OÙ"
              />
              <FilterByOfferTypes
                filterActions={this.filterActions}
                filterState={this.state}
                title="QUOI"
              />
              <div
                id="search-filter-menu-footer-controls"
                className="flex-columns mt18"
              >
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  onClick={this.onResetClick}
                  type="button"
                >
                  Réinitialiser
                </button>
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  onClick={this.onFilterClick}
                  type="button"
                >
                  <span className="is-bold">
Filtrer
                  </span>
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
  dispatch: PropTypes.func.isRequired,
  isVisible: PropTypes.bool.isRequired,
  location: PropTypes.object.isRequired,
  onKeywordsEraseClick: PropTypes.func.isRequired,
  query: PropTypes.object.isRequired,
}

export default compose(
  withQueryRouter,
  connect()
)(SearchFilter)
