/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Icon, Logger, capitalize } from 'pass-culture-shared'

import { navigationLink } from '../utils/geolocation'
import { selectBookables } from '../selectors/selectBookables'
import currentRecommendationSelector from '../selectors/currentRecommendation'

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

  renderOfferWhen() {
    const { bookables, maxDatesShowned } = this.props
    const sliced = bookables.slice(0, maxDatesShowned)
    const hasMoreBookables = bookables.length > maxDatesShowned
    return (
      <div>
        <h3>Quand ?</h3>
        <ul className="dates-info">
          {!sliced ? (
            <li>Plus de dates disponibles :(</li>
          ) : (
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
          )}
        </ul>
      </div>
    )
  }

  renderOfferWhere() {
    const { recommendation } = this.props
    const venue = get(recommendation, 'offer.venue')
    const distance = get(recommendation, 'distance')
    const { address, city, name, postalCode } = venue || {}
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
          <a
            className="distance"
            href={navigationLink(venue.latitude, venue.longitude)}
          >
            {distance}
            <Icon svg="ico-geoloc-solid2" alt="Géolocalisation" />
          </a>
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
  return { bookables, recommendation }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoInfo)
