import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Transition } from 'react-transition-group'

import FilterByDates from './FilterByDates'
import FilterByDistanceContainer from './FilterByDistanceContainer'
import FilterByOfferTypesContainer from './FilterByOfferTypesContainer'
import { getFirstChangingKey, INITIAL_FILTER_PARAMS } from '../helpers'

const filtersPanelHeight = 500
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

class FilterControls extends Component {
  constructor(props) {
    super(props)

    const { query } = props

    this.state = {
      filterParamsMatchingQueryParams: false,
      initialDateParams: true,
      params: query.parse() || {},
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

    this.setState({
      filterParamsMatchingQueryParams: false,
      initialDateParams: true,
      params: query.parse(),
    })
  }

  handleOnClickFilterButton = () => {
    const { resetSearchStore, query, onClickFilterButton, isVisible } = this.props
    const { filterParamsMatchingQueryParams, params } = this.state

    if (filterParamsMatchingQueryParams) {
      resetSearchStore()
    }

    params.page = null
    query.change(params, { pathname: '/recherche/resultats' })
    this.setState({
      initialDateParams: false,
    })
    onClickFilterButton(isVisible)
  }

  handleOnClickReset = () => {
    const { query, resetSearchStore } = this.props

    resetSearchStore()

    this.setState({
      filterParamsMatchingQueryParams: false,
      initialDateParams: true,
      params: {},
    })

    query.change(INITIAL_FILTER_PARAMS, {
      pathname: '/recherche/resultats/tout',
    })
  }

  handleQueryChange = (newValue, callback) => {
    const { query } = this.props
    const { params } = this.state
    const nextFilterParams = { ...params, ...newValue }
    const filterParamsMatchingQueryParams = getFirstChangingKey(query.parse(), newValue)

    this.setState(
      {
        filterParamsMatchingQueryParams,
        params: nextFilterParams,
      },
      callback
    )
  }

  handleQueryAdd = (paramKey, paramValue, callback) => {
    const { params } = this.state
    const encodedValue = encodeURI(paramValue)
    let nextValue = encodedValue
    const previousValue = params[paramKey]

    if (previousValue && previousValue.length) {
      nextValue = previousValue
        .split(',')
        .concat([encodedValue])
        .join(',')
    }

    this.handleQueryChange({ [paramKey]: nextValue }, callback)
  }

  handleQueryRemove = (paramKey, paramValue, callback) => {
    const { params } = this.state
    const previousValue = params[paramKey]

    if (previousValue && previousValue.length) {
      const encodedValue = encodeURI(paramValue)
      const nextValue = previousValue
        .split(',')
        .filter(value => value !== encodedValue)
        .join()

      this.handleQueryChange({ [paramKey]: nextValue === '' ? null : nextValue }, callback)
    }
  }

  render() {
    const { isVisible } = this.props
    const { initialDateParams } = this.state
    const filterActions = {
      add: this.handleQueryAdd,
      change: this.handleQueryChange,
      remove: this.handleQueryRemove,
    }

    return (
      <div className="is-relative is-clipped">
        <Transition
          in={isVisible}
          timeout={transitionDelay}
        >
          {status => (
            <div
              className={`is-full-width transition-status-${status} mb20`}
              id="search-filter-menu"
              style={{ ...defaultStyle, ...transitionStyles[status] }}
            >
              <FilterByDates
                filterActions={filterActions}
                filterState={this.state}
                initialDateParams={initialDateParams}
              />
              <FilterByDistanceContainer
                filterActions={filterActions}
                filterState={this.state}
              />
              <FilterByOfferTypesContainer
                filterActions={filterActions}
                filterState={this.state}
              />
              <div
                className="flex-columns mt18"
                id="search-filter-menu-footer-controls"
              >
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  id="search-filter-reset-button"
                  onClick={this.handleOnClickReset}
                  type="reset"
                >
                  {'Réinitialiser'}
                </button>
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  id="filter-button"
                  onClick={this.handleOnClickFilterButton}
                  type="submit"
                >
                  <span className="is-bold">{'Filtrer'}</span>
                </button>
              </div>
            </div>
          )}
        </Transition>
      </div>
    )
  }
}

FilterControls.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
  onClickFilterButton: PropTypes.func.isRequired,
  query: PropTypes.shape().isRequired,
  resetSearchStore: PropTypes.func.isRequired,
}

export default FilterControls
