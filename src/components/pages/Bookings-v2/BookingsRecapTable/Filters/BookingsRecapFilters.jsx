import React, { Component } from 'react'
import debounce from 'lodash.debounce'
import classnames from 'classnames'

class BookingsRecapFilters extends Component {
  handleOnChange = debounce((value) => {
    const { bookingsRecap } = this.props
    this.filterOffers(bookingsRecap, value)
  }, 300)

  filterOffers = (bookingsRecap, keywords) => {
    const { setFilters } = this.props

    setFilters({ offerName: keywords.toLowerCase() })
  }

  render() {
    return (
      <div className='bookings-recap-filters'>
        <label
          className='select-filters'
          htmlFor='text-filter'
        >
          {'Offre'}
        </label>
        <input
          className='field-input field-text text-filter'
          id='text-filter'
          onChange={(event) => this.handleOnChange(event.target.value)}
          placeholder={"Rechercher par nom d'offre"}
          type='text'
        />
      </div>
    )
  }

}

export default BookingsRecapFilters
