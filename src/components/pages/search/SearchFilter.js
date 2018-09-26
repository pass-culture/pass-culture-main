/* eslint-disable */
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { shallowCompare } from 'react-redux'

import FilterByDates from './FilterByDates'
import FilterByDistance from './FilterByDistance'
import FilterByOfferTypes from './FilterByOfferTypes'

import { INITIAL_FILTER_PARAMS, searchFiltersAdded } from '../search/utils'

function getFirstChangingKey(previousObject, nextObject) {
  return Object.keys(nextObject).find(key => {
    const isNewFalsy = nextObject[key] === null || nextObject[key] === ''
    const isPreviousFalsy =
      typeof previousObject[key] === 'undefined' ||
      previousObject[key] === null ||
      previousObject === ''
    if (isNewFalsy && isPreviousFalsy) {
      return false
    }
    return previousObject[key] !== nextObject[key]
  })
}

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
      filterParams: INITIAL_FILTER_PARAMS,
      isNewFilter: getFirstChangingKey(
        this.props.queryParams,
        INITIAL_FILTER_PARAMS
      ),
    })
  }

  handleFilterParamsChange = (newValue, callback) => {
    const { queryParams } = this.props
    const { filterParams } = this.state

    const nextFilterParams = Object.assign({}, filterParams, newValue)

    const isNewFilter = getFirstChangingKey(queryParams, newValue)

    this.setState(
      {
        filterParams: nextFilterParams,
        isNewFilter,
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
      const args = previousValue.split(',').concat([encodedValue])
      args.sort()
      nextValue = args.join(',')
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

    const isNullFilter = searchFiltersAdded(INITIAL_FILTER_PARAMS, filterParams)

    return (
      <div id="search-filter-menu">
        <FilterByDates
          handleFilterParamsChange={this.handleFilterParamsChange}
          handleFilterParamAdd={this.handleFilterParamAdd}
          handleFilterParamRemove={this.handleFilterParamRemove}
          filterParams={filterParams}
          title="QUAND"
        />
        <FilterByDistance
          handleFilterParamsChange={this.handleFilterParamsChange}
          filterParams={filterParams}
          title="OÙ"
        />
        <FilterByOfferTypes
          handleFilterParamAdd={this.handleFilterParamAdd}
          handleFilterParamRemove={this.handleFilterParamRemove}
          filterParams={filterParams}
          title="QUOI"
        />
        <button
          className="button fs24"
          disabled={isNullFilter}
          onClick={this.onResetClick}
          type="button">
          Réinitialiser
        </button>
        <button
          className="button fs24"
          disabled={!isNewFilter}
          onClick={this.onFilterClick}
          type="button">
          Filtrer
        </button>
      </div>
    )
  }
}

SearchFilter.propTypes = {
  handleQueryParamsChange: PropTypes.func.isRequired,
  queryParams: PropTypes.object.isRequired,
}

export default SearchFilter
