import debounce from 'lodash.debounce'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

import {
  ALL_BOOKING_STATUS,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './_constants'
import FilterByOmniSearch from './FilterByOmniSearch'

class Filters extends Component {
  constructor(props) {
    super(props)
    this.state = {
      filters: {
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
      },
      keywords: EMPTY_FILTER_VALUE,
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    }
  }

  DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

  applyFilters = debounce(filterValues => {
    const { updateGlobalFilters } = this.props
    updateGlobalFilters({
      ...filterValues,
    })
  }, this.DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS)

  // This method is called via Ref
  // eslint-disable-next-line react/no-unused-class-component-methods
  resetAllFilters = () => {
    this.setState(
      {
        filters: {
          bookingBeneficiary: EMPTY_FILTER_VALUE,
          bookingToken: EMPTY_FILTER_VALUE,
          offerISBN: EMPTY_FILTER_VALUE,
          offerName: EMPTY_FILTER_VALUE,
          bookingStatus: [...ALL_BOOKING_STATUS],
        },
        keywords: EMPTY_FILTER_VALUE,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  updateFilters = (updatedFilter, updatedSelectedContent) => {
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          ...updatedFilter,
        },
        ...updatedSelectedContent,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  render() {
    const { isLoading } = this.props
    const { keywords, selectedOmniSearchCriteria } = this.state

    return (
      <div className="filters-wrapper">
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={keywords}
          selectedOmniSearchCriteria={selectedOmniSearchCriteria}
          updateFilters={this.updateFilters}
        />
      </div>
    )
  }
}

Filters.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default Filters
