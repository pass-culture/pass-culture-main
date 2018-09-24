/* eslint-disable */
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { shallowCompare } from 'react-redux'

import FilterByDates from './FilterByDates'
import FilterByDistance from './FilterByDistance'
import FilterByOfferTypes from './FilterByOfferTypes'

class SearchFilter extends Component {
  constructor(props) {
    super(props)
    this.state = {
      filterParams: Object.assign({}, props.queryParams),
      isNewFilter: false,
    }
  }

  componentDidUpdate(prevProps) {
    const { queryParams } = this.props
    // TODO: eslint does not support setState inside componentDidUpdate
    if (queryParams !== prevProps.queryParams) {
      this.setState({
        filterParams: queryParams,
        isNewFilter: false,
      })
    }
  }

  onFilterClick = () => {
    const { handleQueryParamsChange } = this.props
    const { filterParams, isNewFilter } = this.state

    handleQueryParamsChange(filterParams, {
      isRefreshing: isNewFilter,
      pathname: '/recherche/resultats',
    })
  }

  onResetClick = () => {
    this.setState({
      filterParams: this.props.queryParams,
      isNewFilter: false,
    })
  }

  handleFilterParamsChange = (newValue, callback) => {
    const { queryParams } = this.props
    const { filterParams } = this.state

    const atLeastOneChangingKey = Object.keys(newValue).find(
      key =>
        typeof queryParams[key] === 'undefined' ||
        queryParams[key] !== newValue[key]
    )

    const nextFilterParams = Object.assign({}, filterParams, newValue)

    this.setState(
      {
        filterParams: nextFilterParams,
        isNewFilter: typeof atLeastOneChangingKey !== 'undefined',
      },
      callback
    )
  }

  handleFilterParamAdd = (key, value, callback) => {
    const { filterParams } = this.state

    const encodedValue = encodeURI(value)
    let nextValue = encodedValue
    const previousValue = filterParams[key]
    if (get(previousValue, 'length')) {
      nextValue = `${previousValue},${encodedValue}`
    }

    this.handleFilterParamsChange({ [key]: nextValue }, callback)
  }

  handleFilterParamRemove = (key, value, callback) => {
    const { filterParams } = this.state

    const previousValue = filterParams[key]

    if (get(previousValue, 'length')) {
      const encodedValue = encodeURI(value)
      let nextValue = previousValue
        .replace(`,${encodedValue}`, '')
        .replace(encodedValue, '')
      if (nextValue[0] === ',') {
        nextValue = nextValue.slice(1)
      }
      this.handleFilterParamsChange({ [key]: nextValue }, callback)
    }
  }

  render() {
    const { handleClearQueryParams } = this.props
    const { filterParams, isNewFilter } = this.state

    return (
      <div
        id="search-filter-menu"
        className="is-overlay is-clipped flex-columns items-end p12">
        <div className="search-filter">
          <FilterByDates
            handleFilterParamsChange={this.handleFilterParamsChange}
            handleFilterParamAdd={this.handleFilterParamAdd}
            handleFilterParamRemove={this.handleFilterParamRemove}
            filterParams={filterParams}
          />
          <h2>OU</h2>
          <FilterByDistance
            handleFilterParamsChange={this.handleFilterParamsChange}
            filterParams={filterParams}
          />
          <FilterByOfferTypes
            handleFilterParamAdd={this.handleFilterParamAdd}
            handleFilterParamRemove={this.handleFilterParamRemove}
            filterParams={filterParams}
            title="QUOI"
          />
          <button
            className="button"
            disabled={!isNewFilter}
            onClick={this.onResetClick}
            type="button">
            Réinitialiser
          </button>
          <button
            className="button"
            disabled={!isNewFilter}
            onClick={this.onFilterClick}
            type="button">
            Filtrer
          </button>
        </div>
      </div>
    )
  }
}

SearchFilter.propTypes = {
  handleQueryParamsChange: PropTypes.func.isRequired,
  queryParams: PropTypes.object.isRequired,
}

export default SearchFilter
