import get from 'lodash.get'
import PropTypes from 'prop-types'
import React from 'react'
import { capitalize } from 'react-final-form-utils'

import VersoActionsBar from '../VersoActionsBar'
import { getDurationFromMinutes } from './utils'
import Icon from '../../../layout/Icon'
import { navigationLink } from '../../../../utils/geolocation'

class VersoContentOffer extends React.PureComponent {
  componentDidMount() {
    const { handleRequestMusicAndShowTypes } = this.props
    handleRequestMusicAndShowTypes()
  }

  renderOfferDetails() {
    const { recommendation } = this.props
    const description = get(recommendation, 'offer.description')
    if (!description) return null
    return (
      <div>
        <h3>{'Et en détails ?'}</h3>
        <pre
          className="is-raw-description"
          id="verso-offer-description"
        >
          {description}
        </pre>
      </div>
    )
  }

  renderOfferWhat() {
    const {
      musicSubType,
      musicType,
      recommendation,
      showSubType,
      showType,
    } = this.props
    const offer = get(recommendation, 'offer')

    const product = get(offer, 'product')
    const durationMinutes = get(product, 'durationMinutes')
    const duration = getDurationFromMinutes(durationMinutes)

    const extraData = get(product, 'extraData')
    const appLabel = get(product, 'offerType.appLabel')

    const author = get(extraData, 'author')
    const performer = get(extraData, 'performer')
    const speaker = get(extraData, 'speaker')
    const stageDirector = get(extraData, 'stageDirector')
    const type = get(musicType, 'label') || get(showType, 'label')
    const subType = get(musicSubType, 'label') || get(showSubType, 'label')
    return (
      <div>
        <h3>{'Quoi ?'}</h3>
        <div>
          <span
            className="is-bold"
            id="verso-offer-label"
          >
            {appLabel}
          </span>
          {durationMinutes && <span>{' - Durée'} {duration}</span>}
        </div>
        {type && (
          <div>
            {'Genre : '}{type}
            {subType && `/ ${subType}`}
          </div>
        )}
        {author && <div>{'Auteur : '}{author}</div>}
        {performer && <div>{'Interprète : '}{performer}</div>}
        {speaker && <div>{'Intervenant : '}{speaker}</div>}
        {stageDirector && <div>{'Metteur en scène : '}{stageDirector}</div>}
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
            {(!obj.userHasCancelledThisDate && obj.userHasAlreadyBookedThisDate) && ' (réservé)'}
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
          {'Dès maintenant'}
          {limitDatetime && ` et jusqu’au ${limitDatetime}`}{' '}
        </li>
      </React.Fragment>
    )
  }

  renderOfferWhen() {
    const { isFinished } = this.props
    const { recommendation } = this.props
    const isOfferAThing = get(recommendation, 'offer.isThing')

    const offerDateInfos = isOfferAThing
      ? this.renderThingOfferDateInfos()
      : this.renderEventOfferDateInfos()

    return (
      <div>
        <h3>{'Quand ?'}</h3>
        <ul className="dates-info">
          {isFinished ? (
            <li>{'L’offre n’est plus disponible.'}</li>
          ) : (
            offerDateInfos
          )}
        </ul>
      </div>
    )
  }

  renderOfferWhere() {
    const { recommendation } = this.props
    const venue = get(recommendation, 'offer.venue')
    const distance = get(recommendation, 'distance')
    const { address, city, latitude, longitude, name, postalCode, publicName } =
      venue || {}

    return (
      <div>
        <h3>{'Où ?'}</h3>
        <div className="flex-columns flex-between">
          <p className="address-info">
            <span className="is-block">{publicName || name}</span>
            {address && <span className="is-block">{address}</span>}
            {postalCode && <span className="is-block">{postalCode}</span>}
            {city && <span className="is-block">{city}</span>}
          </p>
          {latitude && longitude && (
            <a
              className="distance"
              href={navigationLink(latitude, longitude)}
            >
              <span>{distance}&nbsp;</span>
              <Icon
                alt="Géolocalisation dans Open Street Map"
                svg="ico-geoloc-solid2"
              />
            </a>
          )}
        </div>
      </div>
    )
  }

  render() {
    const { onlineOfferUrl } = this.props
    return (
      <div className="verso-info">
        {onlineOfferUrl && <VersoActionsBar url={onlineOfferUrl} />}
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
  isFinished: false,
  maxShownDates: 7,
  musicSubType: null,
  musicType: null,
  onlineOfferUrl: null,
  recommendation: null,
  showSubType: null,
  showType: null,
}

VersoContentOffer.propTypes = {
  bookables: PropTypes.arrayOf,
  handleRequestMusicAndShowTypes: PropTypes.func.isRequired,
  isFinished: PropTypes.bool,
  maxShownDates: PropTypes.number,
  musicSubType: PropTypes.shape(),
  musicType: PropTypes.shape(),
  onlineOfferUrl: PropTypes.string,
  recommendation: PropTypes.shape(),
  showSubType: PropTypes.shape(),
  showType: PropTypes.shape(),
}

export default VersoContentOffer
