/* eslint
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get'
import { capitalize } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import {
  getDurationFromMinutes,
  getWhatTitleFromLabelAndIsVirtualVenue,
} from './utils'
import { Icon } from '../../layout/Icon'
import { navigationLink } from '../../../utils/geolocation'

class VersoContentOffer extends React.PureComponent {
  renderOfferDetails() {
    const { recommendation } = this.props
    const description = get(recommendation, 'offer.eventOrThing.description')
    if (!description) return null
    return (
      <div>
        <h3>Et en détails ?</h3>
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

  renderEventOfferDateInfos() {
    const { bookables, maxDatesShowned } = this.props
    const sliced = bookables.slice(0, maxDatesShowned)
    const hasMoreBookables = bookables.length > maxDatesShowned
    return (
      <Fragment>
        {sliced.map(obj => (
          <li key={obj.id}>
            {capitalize(obj.humanBeginningDate)}
            {obj.userAsAlreadyReservedThisDate && ' (réservé)'}
          </li>
        ))}
        {hasMoreBookables && (
          <li>{'Cliquez sur "j\'y vais" pour voir plus de dates.'}</li>
        )}
      </Fragment>
    )
  }

  renderThingOfferDateInfos() {
    const { bookables } = this.props
    const limitDatetime = get(bookables, '[0].bookinglimitDatetime')
    return (
      <Fragment>
        <li>
          Dès maintenant {limitDatetime && `et jusqu&apos;au ${limitDatetime}`}{' '}
        </li>
      </Fragment>
    )
  }

  renderOfferWhat() {
    const { recommendation } = this.props
    const eventOrThing = get(recommendation, 'offer.eventOrThing')
    const author = get(eventOrThing, 'author')
    const durationMinutes = get(eventOrThing, 'durationMinutes')
    const isVirtualVenue = get(recommendation, 'offer.venue.isVirtual')
    const label = get(eventOrThing, 'offerType.label')
    const performer = get(eventOrThing, 'performer')
    const speaker = get(eventOrThing, 'speaker')
    const type = get(eventOrThing, 'extraData.musicType')

    const duration = getDurationFromMinutes(durationMinutes)
    const title = getWhatTitleFromLabelAndIsVirtualVenue(label, isVirtualVenue)

    return (
      <div>
        <h3>Quoi ?</h3>
        <span className="is-bold">{title}</span>
        {durationMinutes && <span> - Durée {duration}</span>}
        {type && <span>Genre {type}</span>}
        {author && <span>Auteur {author}</span>}
        {performer && <span>Interprête {performer}</span>}
        {speaker && <span>Intervenant {speaker}</span>}
      </div>
    )
  }

  renderOfferWhen() {
    const { isFinished } = this.props
    const { recommendation } = this.props
    const dateInfosRenderer = (get(recommendation, 'offer.thingId')
      ? this.renderThingOfferDateInfos
      : this.renderEventOfferDateInfos
    ).bind(this)
    return (
      <div>
        <h3>Quand ?</h3>
        <ul className="dates-info">
          {isFinished ? (
            <li>L&apos;offre n&apos;est plus disponible :(</li>
          ) : (
            dateInfosRenderer()
          )}
        </ul>
      </div>
    )
  }

  renderOfferWhere() {
    const { recommendation } = this.props
    const venue = get(recommendation, 'offer.venue')
    const distance = get(recommendation, 'distance')
    const { address, city, latitude, longitude, name, postalCode } = venue || {}
    return (
      <div>
        <h3>Où ?</h3>
        <div className="flex-columns flex-between">
          <p className="address-info">
            {name && <span className="is-block">{name}</span>}
            {address && <span className="is-block">{address}</span>}
            {postalCode && <span className="is-block">{postalCode}</span>}
            {city && <span className="is-block">{city}</span>}
          </p>
          {latitude && longitude && (
            <a className="distance" href={navigationLink(latitude, longitude)}>
              {distance}
              <Icon
                svg="ico-geoloc-solid2"
                alt="Géolocalisation dans Open Street Map"
              />
            </a>
          )}
        </div>
      </div>
    )
  }

  render() {
    return (
      <div className="verso-info">
        {this.renderOfferWhat()}
        {this.renderOfferDetails()}
        {this.renderOfferWhen()}
        {this.renderOfferWhere()}
      </div>
    )
  }
}

VersoContentOffer.defaultProps = {
  bookables: null,
  maxDatesShowned: 7,
  recommendation: null,
}

VersoContentOffer.propTypes = {
  bookables: PropTypes.array,
  isFinished: PropTypes.bool.isRequired,
  maxDatesShowned: PropTypes.number,
  recommendation: PropTypes.object,
}

export default VersoContentOffer
