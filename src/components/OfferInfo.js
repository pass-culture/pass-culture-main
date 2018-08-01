import get from 'lodash.get'
import uniq from 'lodash.uniq'
import moment from 'moment'
import React, { Component } from 'react'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Icon from './layout/Icon'
import Capitalize from './utils/Capitalize'
import bookingsSelector from '../selectors/bookings'
import distanceSelector from '../selectors/distance'
// import currentEventOrThingIdSelector from '../selectors/currentEventOrThingId'
// import currentOfferSelector from '../selectors/currentOffer'
// import currentOffererSelector from '../selectors/currentOfferer'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import currentEventOrThingSelector from '../selectors/currentEventOrThing'
import currentThumbUrlSelector from '../selectors/currentThumbUrl'
import timezoneSelector from '../selectors/currentTimezone'
// import venueSelector from '../selectors/currentVenue'
import { navigationLink } from '../utils/geolocation'

class OfferInfo extends Component {
  render() {
    const {
      bookings,
      distance,
      recommendation,
      thumbUrl,
      tz,
    } = this.props
    const {
      offer
    } = (recommendation || {})
    const {
      eventOrThing,
      venue
    } = (offer || {})
    const {
      description,
    } = (eventOrThing || {})
    const {
      address,
      city,
      managingOfferer,
      name,
      postalCode
    } = (venue || {})

    const NOW = moment()

    const mediatedOccurences = get(recommendation, 'mediatedOccurences', [])
    const bookedDates = bookings.map(b =>
      get(b, 'offer.eventOccurence.beginningDatetime')
    )
    const bookedOfferIds = bookings.map(b => b.offerId)
    const bookableOccurences = mediatedOccurences.filter(
      o =>
        moment(o.offer[0].bookingLimitDatetime).isAfter(NOW) &&
        !(o.id in bookedOfferIds)
    )

    const infos = {
      image: thumbUrl,
      description,
      what: description
        ? ''
        : get(offer, 'eventOccurence.event.description'),
      when: uniq(
        bookableOccurences
          .map(o => o.beginningDatetime)
          .sort()
          .slice(0, 7)
          .concat(bookedDates)
          .sort()
      ),
      where: {
        name,
        address:
          address +
          ',' +
          (postalCode || '') +
          ',' +
          (city || ''),
      },
    }

    return (
      <div className="offer-info">
        {managingOfferer && (
          <div className="offerer">Ce livre vous est offert par {managingOfferer}.</div>
        )}
        {false && <img alt="" className="offerPicture" src={infos.image} />}
        {infos.description && (
          <div className="description">
            {infos.description.split('\n').map((p, index) => (
              <p key={index}>{p}</p>
            ))}
          </div>
        )}
        {infos.what && (
          <div>
            <h3>Quoi ?</h3>
            <p>{infos.what}</p>
          </div>
        )}
        {infos.when && (
          <div>
            <h3>Quand ?</h3>
            <ul className="dates-info">
              {infos.when.length === 0 && <li>Plus de dates disponibles :(</li>}
              {infos.when.map((occurence, index) => (
                <li key={index}>
                  <Capitalize>
                    {tz &&
                      moment(occurence)
                        .tz(tz)
                        .format('dddd DD/MM/YYYY à H:mm')}
                  </Capitalize>
                  {bookedDates.indexOf(occurence) > -1 && ' (réservé)'}
                </li>
              ))}
              {bookableOccurences.length > 7 && (
                <li>Cliquez sur "j'y vais" pour voir plus de dates.</li>
              )}
            </ul>
          </div>
        )}
        {infos.where.name &&
          infos.where.address && (
            <div>
              <h3>Où ?</h3>
              <a
                className="distance"
                href={navigationLink(venue.latitude, venue.longitude)}>
                {distance}
                <Icon svg="ico-geoloc-solid2" alt="Géolocalisation" />
              </a>
              <ul className="address-info">
                <li>{infos.where.name}</li>
                {infos.where.address.split(/[,\n\r]/).map((el, index) => (
                  <li key={index}>
                    <Capitalize>{el}</Capitalize>
                  </li>
                ))}
              </ul>
            </div>
          )}
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      const eventOrThing = currentEventOrThingSelector(state, offerId, mediationId)
      return {
        bookings: bookingsSelector(state, get(eventOrThing, 'id')),
        distance: distanceSelector(state, offerId, mediationId),
        // offer: currentOfferSelector(state),
        // offerer: currentOffererSelector(state),
        // eventOrThing: currentEventOrThingSelector(state, offerId, mediationId),
        thumbUrl: currentThumbUrlSelector(state, offerId, mediationId),
        recommendation: currentRecommendationSelector(state, offerId, mediationId),
        // venue: venueSelector(state, offerId, mediationId),
        tz: timezoneSelector(state),
      }
  })
)(OfferInfo)
