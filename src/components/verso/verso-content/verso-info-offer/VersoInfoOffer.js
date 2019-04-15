import get from 'lodash.get'
import { Icon, Logger, capitalize } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'

import { navigationLink } from '../../../../utils/geolocation'

class VersoInfoOffer extends React.PureComponent {
  componentWillMount() {
    Logger.fixme('VersoInfoOffer ---> componentWillMount')
  }

  componentWillUnmount() {
    Logger.fixme('VersoInfoOffer ---> componentWillUnmount')
  }

  renderOfferWhat() {
    const { recommendation } = this.props
    const description = get(recommendation, 'offer.eventOrThing.description')

    if (!description) return null

    return (
      <div>
        <h3>Quoi ?</h3>
        <pre className="is-raw-description">{description}</pre>
      </div>
    )
  }

  renderEventOfferDateInfos() {
    const { bookables, maxShownDates } = this.props
    const sliced = bookables.slice(0, maxShownDates)
    const hasMoreBookables = bookables.length > maxShownDates

    return (
      <React.Fragment>
        {sliced.map(obj => (
          <li key={obj.id}>
            {capitalize(obj.humanBeginningDate)}
            {obj.userAsAlreadyReservedThisDate && ' (réservé)'}
          </li>
        ))}
        {hasMoreBookables && (
          <li>{'Cliquez sur "j\'y vais" pour voir plus de dates.'}</li>
        )}
      </React.Fragment>
    )
  }

  renderThingOfferDateInfos() {
    const { bookables } = this.props
    const limitDatetime = get(bookables, '[0].bookinglimitDatetime')
    return (
      <React.Fragment>
        <li>
          Dès maintenant
          {limitDatetime && ` et jusqu&apos;au ${limitDatetime}`}
          {' '}
        </li>
      </React.Fragment>
    )
  }

  renderOfferWhen() {
    const { isFinished } = this.props
    const { recommendation } = this.props
    const renderDateInfos = (get(recommendation, 'offer.thingId')
      ? this.renderThingOfferDateInfos
      : this.renderEventOfferDateInfos
    ).bind(this)

    return (
      <div>
        <h3>Quand ?</h3>
        <ul className="dates-info">
          {isFinished ? (
            <li>L&apos;offre n&apos;est plus disponible.</li>
          ) : (
            renderDateInfos()
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
              <span>
                {distance}
                {''}
              </span>
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
        {this.renderOfferWhen()}
        {this.renderOfferWhere()}
      </div>
    )
  }
}

VersoInfoOffer.defaultProps = {
  bookables: null,
  maxShownDates: 7,
  recommendation: null,
}

VersoInfoOffer.propTypes = {
  bookables: PropTypes.array,
  isFinished: PropTypes.bool.isRequired,
  maxShownDates: PropTypes.number,
  recommendation: PropTypes.object,
}

export default VersoInfoOffer
