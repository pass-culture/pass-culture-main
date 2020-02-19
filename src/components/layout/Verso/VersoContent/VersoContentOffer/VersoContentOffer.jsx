import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'

import { navigationLink } from '../../../../../utils/geolocation'
import DuoOfferContainer from '../../../DuoOffer/DuoOfferContainer'
import Icon from '../../../Icon/Icon'
import getDurationFromMinutes from './utils/getDurationFromMinutes'
import VersoActionsBar from './VersoActionsBar/VersoActionsBar'
import { capitalize } from '../../../../../utils/react-form-utils/functions'

const UNKNOWN_DISTANCE = '-'

class VersoContentOffer extends PureComponent {
  componentDidMount() {
    const { handleRequestMusicAndShowTypes } = this.props

    handleRequestMusicAndShowTypes()
  }

  renderOfferDetails() {
    const { offer } = this.props
    const { description } = offer || {}

    if (!description) return null

    return (
      <Fragment>
        <h3>
          {'Et en détails ?'}
        </h3>
        <pre
          className="is-raw-description"
          id="verso-offer-description"
        >
          {description}
        </pre>
      </Fragment>
    )
  }

  renderOfferWhat() {
    const { offer, style } = this.props
    const { durationMinutes, extraData, offerType } = offer || {}
    const { author, performer, speaker, stageDirector } = extraData || {}
    const { appLabel } = offerType || {}
    const duration = getDurationFromMinutes(durationMinutes)

    return (
      <Fragment>
        <h3>
          {'Quoi ?'}
        </h3>
        <div>
          <span
            className="is-bold"
            id="verso-offer-label"
          >
            {appLabel}
          </span>
          {durationMinutes && <span>
            {` - Durée ${duration}`}
          </span>}
        </div>
        {style && <div>
          {`Genre : ${style}`}
        </div>}
        {author && <div>
          {`Auteur : ${author}`}
        </div>}
        {performer && <div>
          {`Interprète : ${performer}`}
        </div>}
        {speaker && <div>
          {`Intervenant : ${speaker}`}
        </div>}
        {stageDirector && <div>
          {`Metteur en scène : ${stageDirector}`}
        </div>}
        {offer.id && (
          <DuoOfferContainer
            label="Vous pouvez réserver deux places."
            offerId={offer.id}
          />
        )}
      </Fragment>
    )
  }

  renderEventOfferDateInfos() {
    const { bookables, maxShownDates } = this.props
    const slicedBookables = bookables.slice(0, maxShownDates)
    const hasMoreBookables = bookables.length > maxShownDates

    return (
      <Fragment>
        {slicedBookables.map(bookable => (
          <li key={bookable.id}>
            {capitalize(bookable.humanBeginningDate)}
            {!bookable.userHasCancelledThisDate &&
              bookable.userHasAlreadyBookedThisDate &&
              ' (réservé)'}
          </li>
        ))}
        {hasMoreBookables && <li>
          {'Cliquez sur "j’y vais" pour voir plus de dates.'}
        </li>}
      </Fragment>
    )
  }

  renderThingOfferDateInfos() {
    const { bookables } = this.props
    const atLeastOneBookable = bookables.length > 0
    const limitDatetime = atLeastOneBookable ? bookables[0].bookinglimitDatetime : null

    return (<li>
      {`Dès maintenant${limitDatetime ? ` et jusqu’au ${limitDatetime}` : ''}`}
    </li>)
  }

  renderOfferWhen() {
    const { isNotBookable, offer } = this.props
    const { isThing } = offer || {}

    const offerDateInfos = isThing
      ? this.renderThingOfferDateInfos()
      : this.renderEventOfferDateInfos()

    return (
      <Fragment>
        <h3>
          {'Quand ?'}
        </h3>
        <ul className="dates-info">
          {isNotBookable ? <li>
            {'L’offre n’est plus disponible.'}
          </li> : offerDateInfos}
        </ul>
      </Fragment>
    )
  }

  renderOfferWhere() {
    const { distance, offer, userGeolocation } = this.props
    const { venue } = offer || {}
    const { address, city, latitude, longitude, name, postalCode, publicName } = venue || {}
    const isNotDigitalOffer = latitude && longitude

    return (
      <Fragment>
        <div className="flex-columns flex-between">
          <h3>
            {'Où ?'}
          </h3>
          {isNotDigitalOffer && (
            <span className="vco-distance">
              <Icon
                className="vco-geolocation-icon"
                svg="ico-geoloc"
              />
              <span>
                {distance === UNKNOWN_DISTANCE ? UNKNOWN_DISTANCE : `À ${distance}`}
              </span>
            </span>
          )}
        </div>
        <address>
          {publicName || name}
          <br />
          {address && (
            <Fragment>
              {address}
              <br />
            </Fragment>
          )}
          {postalCode && (
            <Fragment>
              {postalCode}
              <br />
            </Fragment>
          )}
          {city && (
            <Fragment>
              {city}
              <br />
            </Fragment>
          )}
        </address>
        {isNotDigitalOffer && (
          <a
            className="vco-itinerary"
            href={navigationLink(latitude, longitude, userGeolocation)}
            rel="noopener noreferrer"
            target="_blank"
            title="Ouverture de votre gestionnaire de carte dans une nouvelle fenêtre"
          >
            <Icon
              className="vco-geolocation-icon"
              svg="ico-go"
            />
            <span>
              {'Itinéraire'}
            </span>
          </a>
        )}
      </Fragment>
    )
  }

  render() {
    const { booking, isCancelled } = this.props
    const { completedUrl } = booking || {}

    return (
      <div className="verso-info">
        {isCancelled === false && completedUrl && <VersoActionsBar url={completedUrl} />}
        {this.renderOfferWhat()}
        {this.renderOfferDetails()}
        {this.renderOfferWhen()}
        {this.renderOfferWhere()}
      </div>
    )
  }
}

VersoContentOffer.defaultProps = {
  booking: null,
  isCancelled: true,
  isNotBookable: false,
  maxShownDates: 7,
  offer: null,
  style: ''
}

VersoContentOffer.propTypes = {
  bookables: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  booking: PropTypes.shape(),
  distance: PropTypes.string.isRequired,
  handleRequestMusicAndShowTypes: PropTypes.func.isRequired,
  isCancelled: PropTypes.bool,
  isNotBookable: PropTypes.bool,
  maxShownDates: PropTypes.number,
  offer: PropTypes.shape({
    id: PropTypes.string,
    product: PropTypes.shape()
  }),
  style: PropTypes.string,
  userGeolocation: PropTypes.shape().isRequired
}

export default VersoContentOffer
