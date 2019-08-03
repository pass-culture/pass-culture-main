import moment from 'moment'
import { capitalize } from 'react-final-form-utils'
import { connect } from 'react-redux'

import MyBooking from './MyBooking'
import { humanizeRelativeDate } from '../../../../utils/date/date'
import { getTimezone } from '../../../../utils/timezone'
import { versoUrl } from '../../../../utils/url/url'

export const stringify = date => timeZone =>
  capitalize(
    moment(date)
      .tz(timeZone)
      .format('dddd DD/MM/YYYY à H:mm')
  )

export const updatePropsWithDateElements = (beginningDateTime, departementCode) => {
  const timeZone = getTimezone(departementCode)
  let stringifyDate = 'Permanent'

  if (beginningDateTime) {
    stringifyDate = stringify(beginningDateTime)(timeZone)
  }

  return stringifyDate
}

export const isFinished = endDateTime =>
  endDateTime !== null && new Date(endDateTime).getTime() - Date.now() < 0

export const ribbonLabelAndType = (isCancelled, isFinished, humanizeRelativeDate = '') => {
  if (!isCancelled && humanizeRelativeDate === 'Aujourd’hui') {
    return {
      label: 'Aujourd’hui',
      type: 'today',
    }
  } else if (!isCancelled && humanizeRelativeDate === 'Demain') {
    return {
      label: 'Demain',
      type: 'tomorrow',
    }
  } else if (!isCancelled && isFinished) {
    return {
      label: 'Terminé',
      type: 'finished',
    }
  } else if (isCancelled) {
    return {
      label: 'Annulé',
      type: 'cancelled',
    }
  }

  return null
}

export const mapStateToProps = (state, ownProps) => {
  const { booking } = ownProps
  const { isCancelled, stock } = booking
  const { beginningDatetime: beginningDateTime, endDatetime: endDateTime } = stock
  const {
    resolvedOffer: {
      id: offerId = '',
      product: { name = '' },
      venue: { departementCode = '' },
    },
  } = stock
  const {
    recommendation: { mediationId = '', thumbUrl = '' },
    token = '',
  } = booking

  return {
    name,
    versoUrl: versoUrl(offerId, mediationId),
    thumbUrl,
    token: token.toLowerCase(),
    ribbon: ribbonLabelAndType(
      isCancelled,
      isFinished(endDateTime),
      humanizeRelativeDate(beginningDateTime)
    ),
    stringifyDate: updatePropsWithDateElements(beginningDateTime, departementCode),
  }
}

export default connect(mapStateToProps)(MyBooking)
