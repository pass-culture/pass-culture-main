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
  onFilterChange = typeSublabel => {
    const {
      handleFilterParamsChange,
      handleFilterParamAdd,
      handleFilterParamRemove,
      filterParams,
    } = this.props

    const daysSegmentsValue = decodeURI(filterParams.days_segments || '')
    const isAlreadyIncluded = daysSegmentsValue.includes(typeSublabel)

    // WE ADD THE DATE AT THE FIRST DAYS SEGMENTS CLICKED
    // WE REMOVE THE DATE AT THE LAST DAYS SEGMENTS CLICKED
    let callback
    if (!get(daysSegmentsValue, 'length')) {
      const date = moment(moment.now()).toISOString()
      callback = () => handleFilterParamsChange({ date })
    } else if (isAlreadyIncluded && daysSegmentsValue.split(',').length === 1) {
      console.log('ON ENLEVE')
      callback = () => handleFilterParamsChange({ date: null })
    }

    if (isAlreadyIncluded) {
      handleFilterParamRemove('days_segments', typeSublabel, callback)
      return
    }

    handleFilterParamAdd('days_segments', typeSublabel, callback)
  }

  render() {
    const { filterParams } = this.props

    const daysSegmentsValue = decodeURI(filterParams.days_segments || '')

    return (
      <div>
        <h2>
DATE (Scrollable horizontally)
        </h2>
        {checkboxes.map(({ label, value }) => (
          <div className="field field-checkbox" key={value}>
            <label className="label"> 
              {' '}
              {label}
            </label>
            <input
              checked={daysSegmentsValue.includes(value)}
              className="input is-normal"
              onChange={() => this.onFilterChange(value)}
              type="checkbox"
            />
          </div>
        ))}
        <div>
Par date
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
