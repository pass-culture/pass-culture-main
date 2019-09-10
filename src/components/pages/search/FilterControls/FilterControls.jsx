import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Transition } from 'react-transition-group'

import FilterByDates from './FilterByDates'
import FilterByDistanceContainer from './FilterByDistanceContainer'
import FilterByOfferTypesContainer from './FilterByOfferTypesContainer'
import { getCanFilter, getVisibleParamsAreEmpty, INITIAL_FILTER_PARAMS } from '../helpers'

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
      shouldResetDate: true,
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
      shouldResetDate: true,
      params: query.parse(),
    })
  }

  handleOnClickFilterButton = () => {
    const { isVisible, onClickFilterButton, query } = this.props
    const { params } = this.state

    params.page = null
    query.change(params, { pathname: '/recherche/resultats' })
    this.setState({
      shouldResetDate: false,
    })
    onClickFilterButton(isVisible)
  }

  handleOnClickReset = () => {
    const { query } = this.props

    this.setState({
      shouldResetDate: true,
      params: {},
    })

    const nextQueryParams = { ...INITIAL_FILTER_PARAMS, page: null }
    query.change(nextQueryParams)
  }

  handleQueryChange = (newValue, callback) => {
    const { params } = this.state
    const nextFilterParams = { ...params, ...newValue }
    this.setState(
      {
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
    const { isVisible, query } = this.props
    const { shouldResetDate, params } = this.state
    const filterParamsAreEmpty = getVisibleParamsAreEmpty(params)
    const canFilter = getCanFilter(params, query.parse())

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
                shouldResetDate={shouldResetDate}
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
                  disabled={filterParamsAreEmpty}
                  id="search-filter-reset-button"
                  onClick={this.handleOnClickReset}
                  type="reset"
                >
                  {'Réinitialiser'}
                </button>
                <button
                  className="no-background no-outline col-1of2 fs20 py12"
                  disabled={!canFilter}
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
}

export default FilterControls
