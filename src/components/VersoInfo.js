import PropTypes from 'prop-types'
import get from 'lodash.get'
import uniq from 'lodash.uniq'
import moment from 'moment'
import { capitalize, Icon, Logger } from 'pass-culture-shared'
import React from 'react'
import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import ReactMarkdown from 'react-markdown'

import bookingsSelector from '../selectors/bookings'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import { navigationLink } from '../utils/geolocation'

const renderDescription = desc => (
  <div className="description">
    <ReactMarkdown source={desc.split('\n').join('\n\n')} />
  </div>
)

const renderVenueDetails = (venue, distance, where) => (
  <div>
    <h3>
      {'Où ?'}
    </h3>
    <a
      className="distance"
      href={navigationLink(venue.latitude, venue.longitude)}
    >
      {distance}
      <Icon svg="ico-geoloc-solid2" alt="Géolocalisation" />
    </a>
    <ul className="address-info">
      <li>
        {where.name}
      </li>
      {where.address.split(/[,\n\r]/).map((el, index) => (
        // eslint-disable-next-line react/no-array-index-key
        <li key={index}>
          {capitalize(el)}
        </li>
      ))}
    </ul>
  </div>
)

const VersoInfo = ({ bookings, currentRecommendation }) => {
  const { distance, offer, thumbUrl, tz } = currentRecommendation || {}
  const { eventOrThing, venue } = offer || {}
  const { description } = eventOrThing || {}
  const { address, city, managingOfferer, name, postalCode } = venue || {}

  const NOW = moment()

  const mediatedOccurences = get(
    currentRecommendation,
    'mediatedOccurences',
    []
  )
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
    description,
    image: thumbUrl,
    what: description ? '' : get(offer, 'eventOccurence.event.description'),
    when: uniq(
      bookableOccurences
        .map(o => o.beginningDatetime)
        .sort()
        .slice(0, 7)
        .concat(bookedDates)
        .sort()
    ),
    where: {
      address: `${address},${postalCode || ''},${city || ''}`,
      name,
    },
  }
  Logger.fixme('Verso info is mounted but not visible')
  return (
    <div className="verso-info">
      {managingOfferer && (
        <div className="offerer">
          Ce livre vous est offert par 
          {' '}
          {managingOfferer}
.
        </div>
      )}
      {false && <img alt="" className="offerPicture" src={infos.image} />}
      {infos.description && renderDescription(infos.description)}
      {infos.what && (
        <div>
          <h3>
Quoi ?
          </h3>
          <p>
            {infos.what}
          </p>
        </div>
      )}
      {infos.when && (
        <div>
          <h3>
Quand ?
          </h3>
          <ul className="dates-info">
            {infos.when.length === 0 && (
            <li>
Plus de dates disponibles :(
            </li>
)}
            {infos.when.map((occurence, index) => (
              // eslint-disable-next-line react/no-array-index-key
              <li key={index}>
                {tz &&
                  capitalize(
                    moment(occurence)
                      .tz(tz)
                      .format('dddd DD/MM/YYYY à H:mm')
                  )}
                {bookedDates.indexOf(occurence) > -1 && ' (réservé)'}
              </li>
            ))}
            {bookableOccurences.length > 7 && (
              <li>
                {'Cliquez sur "j\'y vais" pour voir plus de dates.'}
              </li>
            )}
          </ul>
        </div>
      )}
      {infos.where.name &&
        infos.where.address &&
        renderVenueDetails(venue, distance, infos.where)}
    </div>
  )
}

VersoInfo.defaultProps = {
  currentRecommendation: null,
}

VersoInfo.propTypes = {
  bookings: PropTypes.array.isRequired,
  currentRecommendation: PropTypes.object,
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    const currentRecommendation = currentRecommendationSelector(
      state,
      offerId,
      mediationId
    )
    const eventOrThingId = get(currentRecommendation, 'offer.eventOrThing.id')
    return {
      bookings: bookingsSelector(state, eventOrThingId),
      currentRecommendation,
    }
  })
)(VersoInfo)
