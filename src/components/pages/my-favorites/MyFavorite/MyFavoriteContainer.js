import moment from 'moment'
import { capitalize } from 'react-final-form-utils'
import { connect } from 'react-redux'

import MyFavorite from './MyFavorite'
import { getTimezone } from '../../../../utils/timezone'

export const stringify = date => timeZone =>
  capitalize(
    moment(date)
      .tz(timeZone)
      .format('dddd DD/MM/YYYY à H:mm')
  )

export const updatePropsWithDateElements = (props, beginningDateTime, departementCode) => {
  const timeZone = getTimezone(departementCode)
  const stringifyDate = stringify(beginningDateTime)(timeZone)

  return { ...props, stringifyDate }
}

export const urlOf = myFavorite => {
  const {mediationId, offer: id} = myFavorite
  const urlElements = ['', 'decouverte', id, 'verso']
  if (mediationId) {
    urlElements.splice(3, 0, mediationId)
  }

  return urlElements.join('/')
}

export const mapStateToProps = (state, ownProps) => {
  const { favorite } = ownProps
  const { mediation, offer} = favorite || {}
  const { name } = offer
  const { thumbUrl } = mediation

  return {
    name: name,
    offerVersoUrl: urlOf(favorite),
    thumbUrl: thumbUrl,
  }
}

export default connect(mapStateToProps)(MyFavorite)
