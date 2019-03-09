/* eslint
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get'
import { Icon, Logger, capitalize } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { navigationLink } from '../../utils/geolocation'
import { isRecommendationFinished } from '../../helpers'
import { selectBookables } from '../../selectors/selectBookables'
import currentRecommendationSelector from '../../selectors/currentRecommendation'

class VersoInfo extends React.PureComponent {
  componentWillMount() {
    Logger.fixme('VersoInfo ---> componentWillMount')
  }

  componentWillUnmount() {
    Logger.fixme('VersoInfo ---> componentWillUnmount')
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
          Dès maintenant {limitDatetime && `et jusqu&apos;au ${limitDatetime}`}{' '}
        </li>
      </React.Fragment>
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
        {this.renderOfferWhen()}
        {this.renderOfferWhere()}
      </div>
    )
  }
}

VersoInfo.defaultProps = {
  bookables: null,
  maxDatesShowned: 7,
  recommendation: null,
}

VersoInfo.propTypes = {
  bookables: PropTypes.array,
  isFinished: PropTypes.bool.isRequired,
  maxDatesShowned: PropTypes.number,
  recommendation: PropTypes.object,
}

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { mediationId, offerId } = match.params
  // recuperation de la recommandation
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )

  const bookables = selectBookables(state, recommendation, match)
  const isFinished = isRecommendationFinished(recommendation, offerId)
  return {
    bookables,
    isFinished,
    recommendation,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoInfo)
