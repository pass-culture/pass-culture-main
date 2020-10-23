import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import DateField from 'components/layout/form/fields/DateField/DateField'
import TimeField from 'components/layout/form/fields/TimeField'

const EventFields = ({ beginningMinDate, readOnly, stocks, timezone }) => {
  const highlightDates = (stocks || []).map(stock => stock.beginningDatetime)

  return (
    <Fragment>
      <td>
        <DateField
          highlightDates={highlightDates}
          minDate={beginningMinDate || moment()}
          name="beginningDatetime"
          readOnly={readOnly}
          required
          timezone={timezone}
          title="Date"
        />
      </td>
      <td>
        <TimeField
          name="beginningTime"
          patchKey="beginningDatetime"
          readOnly={readOnly}
          required
          title="Heure"
        />
      </td>
    </Fragment>
  )
}

EventFields.defaultProps = {
  beginningMinDate: null,
  readOnly: true,
  stocks: null,
  timezone: null,
}

EventFields.propTypes = {
  beginningMinDate: PropTypes.string,
  readOnly: PropTypes.bool,
  stocks: PropTypes.arrayOf(PropTypes.shape()),
  timezone: PropTypes.string,
}

export default EventFields
