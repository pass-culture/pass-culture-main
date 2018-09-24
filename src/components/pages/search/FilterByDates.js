import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

const checkboxes = [
  {
    label: 'Tout de suite !',
    value: '0-1',
  },
  {
    label: 'Entre 1 et 5 jours',
    value: '1-5',
  },
  {
    label: 'Plus de 5 jours',
    // will the pass culture live for ever?
    // guess that 273 years are enough
    value: '5-100000',
  },
]

class FilterByDates extends Component {
  onFilterChange = day => {
    const {
      handleFilterParamsChange,
      handleFilterParamAdd,
      handleFilterParamRemove,
      filterParams,
    } = this.props

    const days = decodeURI(filterParams.jours || '')
    const isAlreadyIncluded = days.includes(day)

    // WE ADD THE DATE AT THE FIRST DAYS SEGMENTS CLICKED
    // WE REMOVE THE DATE AT THE LAST DAYS SEGMENTS CLICKED
    let callback
    if (!get(days, 'length')) {
      const date = moment(moment.now()).toISOString()
      callback = () => handleFilterParamsChange({ date })
    } else if (isAlreadyIncluded && days.split(',').length === 1) {
      callback = () => handleFilterParamsChange({ date: null })
    }

    if (isAlreadyIncluded) {
      handleFilterParamRemove('jours', day, callback)
      return
    }

    handleFilterParamAdd('jours', day, callback)
  }

  render() {
    const { filterParams } = this.props

    const days = decodeURI(filterParams.jours || '')

    return (
      <div className="dotted-bottom-primary">
        <h2 className="fs18">
QUAND
        </h2>
        {checkboxes.map(({ label, value }) => (
          <div id="date-checkbox">
            <div className="field field-checkbox" key={value}>
              <label className="label fs22"> 
                {' '}
                {label}
              </label>
              <input
                checked={days.includes(value)}
                className="input is-normal"
                onChange={() => this.onFilterChange(value)}
                type="checkbox"
              />
            </div>
          </div>
        ))}
        <div>
Par date TO DO
        </div>
      </div>
    )
  }
}

FilterByDates.propTypes = {
  filterParams: PropTypes.object.isRequired,
  handleFilterParamAdd: PropTypes.func.isRequired,
  handleFilterParamRemove: PropTypes.func.isRequired,
  handleFilterParamsChange: PropTypes.func.isRequired,
}

export default FilterByDates
