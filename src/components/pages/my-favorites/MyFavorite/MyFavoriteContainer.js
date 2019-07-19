import moment from 'moment'
import { capitalize } from 'react-final-form-utils'
import { connect } from 'react-redux'

import MyFavorite from './MyFavorite'
import get from "lodash.get";
import {computeDistanceInMeters, humanizeDistance} from "../../../../utils/geolocation";
import {humanizeBeginningDate, markAsBooked} from "../../../../selectors/selectBookables";

export const stringify = date => timeZone =>
  capitalize(
    moment(date)
      .tz(timeZone)
      .format('dddd DD/MM/YYYY à H:mm')
  )


export const urlOf = myFavorite => {
  const {mediationId, offerId} = myFavorite
  const urlElements = ['', 'decouverte', offerId, 'verso']
  if (mediationId) {
    urlElements.splice(3, 0, mediationId)
  }

  return urlElements.join('/')
}

export const mapStateToProps = (state, ownProps) => {
  const { favorite } = ownProps
  const { mediation, offer } = favorite || {}
  const { name, venue, isFinished, stocks, isFullyBooked } = offer
  const type = get(offer.product, 'offerType.appLabel')
  const { thumbUrl } = mediation

  const offerDateInfos = get(offer, 'dateRange[0]')
  const latitude = state.geolocation.latitude
  const longitude = state.geolocation.longitude

  const isBooked = stocks.some( stock => {
    return stock.bookings.length > 0
  })

  const offerDate = new Date(offerDateInfos)
  const today = new Date()
  const delta = Math.round((offerDate.getTime() - today.getTime()) / 1000)

  const minute = 60,
    hour = minute * 60,
    day = hour * 24,
    week = day * 7

  let relativeDate

  if (delta > 0 && delta < day) {
    relativeDate = "AUJOURD'HUI";
  } else if (delta > day * 1) {
    relativeDate = 'DEMAIN';
  } else if (delta > week) {
    relativeDate = 'SEMAINE PROCHAINE';
  }

  let distance
  if (!latitude || !longitude || !offer || !venue) {
    distance = '-'
  } else {
    const distanceInMeters = computeDistanceInMeters(
      latitude,
      longitude,
      venue.latitude,
      venue.longitude
    )
    distance = humanizeDistance(distanceInMeters)
  }

  return {
    name: name,
    type: type,
    dateInfos: offerDateInfos,
    distance: distance,
    isFinished: isFinished,
    isBooked: isBooked,
    isFullyBooked: isFullyBooked,
    relativeDate: relativeDate,
    offerVersoUrl: urlOf(favorite),
    thumbUrl: thumbUrl,
  }
}

export default connect(mapStateToProps)(MyFavorite)
