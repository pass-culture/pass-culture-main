/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
// import uniq from 'lodash.uniq'
// import moment from 'moment'
import { Icon, Logger } from 'pass-culture-shared'
import React from 'react'
import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
// import ReactMarkdown from 'react-markdown'

import { selectBookings } from '../selectors/selectBookings'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import { navigationLink } from '../utils/geolocation'

class VersoInfo extends React.PureComponent {
  componentWillMount() {
    Logger.fixme('VersoInfo ---> componentWillMount')
  }

  componentWillUnmount() {
    Logger.fixme('VersoInfo ---> componentWillUnmount')
  }

  renderOfferWhat() {
    const { recommendation } = this.props
    const { description } = get(recommendation, 'offer.eventOrThing')
    if (!description) return null
    return (
      <div>
        <h3>Quoi ?</h3>
        <pre className="is-raw-description">{description}</pre>
      </div>
    )
  }

  renderOfferWho() {
    const { recommendation } = this.props
    const managingOfferer = get(recommendation, 'offer.venue.managingOfferer')
    if (!managingOfferer) return null
    return (
      <div className="offerer">
        Ce livre vous est offert par {managingOfferer}.
      </div>
    )
  }

  renderOfferWhen() {
    // const now = moment()
    const { recommendation } = this.props
    console.log('recommendation', recommendation)
    // const tz = get(recommendation, 'tz')

    // const mediatedOccurences = get(recommendation, 'mediatedOccurences', [])
    // const bookedDates = bookings.map(b =>
    //   get(b, 'offer.eventOccurence.beginningDatetime')
    // )
    // const bookedOfferIds = bookings.map(b => b.offerId)
    // const bookableOccurences = mediatedOccurences.filter(
    //   o =>
    //     moment(o.offer[0].bookingLimitDatetime).isAfter(now) &&
    //     !(o.id in bookedOfferIds)
    // )

    // when: uniq(
    //   bookableOccurences
    //     .map(o => o.beginningDatetime)
    //     .sort()
    //     .slice(0, 7)
    //     .concat(bookedDates)
    //     .sort()
    // ),
    return (
      <div>
        <h3>Quand ?</h3>
        <ul className="dates-info">
          {/* {infos.when.length === 0 && <li>Plus de dates disponibles :(</li>}
          {infos.when.map((occurence, index) => (
            // FIXME ->
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
          ))} */}
          {/* {bookableOccurences.length > 7 && (
            <li>{'Cliquez sur "j\'y vais" pour voir plus de dates.'}</li>
          )} */}
        </ul>
      </div>
    )
  }

  renderOfferWhere = () => {
    const { recommendation } = this.props
    const venue = get(recommendation, 'offer.venue')
    const distance = get(recommendation, 'distance')
    const { address, city, name, postalCode } = venue || {}
    return (
      <div>
        <h3>Où ?</h3>
        <a
          className="distance"
          href={navigationLink(venue.latitude, venue.longitude)}
        >
          {distance}
          <Icon svg="ico-geoloc-solid2" alt="Géolocalisation" />
        </a>
        <p className="address-info">
          {/* {capitalize} */}
          <span className="is-block">{name}</span>
          <span className="is-block">{address}</span>
          <span className="is-block">{postalCode}</span>
          <span className="is-block">{city}</span>
        </p>
      </div>
    )
  }

  render() {
    return (
      <div className="verso-info">
        {this.renderOfferWhat()}
        {this.renderOfferWhen()}
        {this.renderOfferWhere()}
      </div>
    )
  }
}

VersoInfo.defaultProps = {
  recommendation: null,
}

VersoInfo.propTypes = {
  // bookings: PropTypes.array.isRequired,
  recommendation: PropTypes.object,
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    const recommendation = currentRecommendationSelector(
      state,
      offerId,
      mediationId
    )
    const eventOrThingId = get(recommendation, 'offer.eventOrThing.id')
    return {
      bookings: selectBookings(state, eventOrThingId),
      recommendation,
    }
  })
)(VersoInfo)
