import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'

import { navigationLink } from '../../../../../utils/geolocation'
import { capitalize } from '../../../../../utils/react-form-utils/functions'
import DuoOfferContainer from '../../../DuoOffer/DuoOfferContainer'
import Icon from '../../../Icon/Icon'
import getDurationFromMinutes from './utils/getDurationFromMinutes'
import VersoActionsBar from './VersoActionsBar/VersoActionsBar'

class VersoContentOffer extends PureComponent {
  componentDidMount() {
    const { handleRequestMusicAndShowTypes } = this.props

    handleRequestMusicAndShowTypes()
  }

  renderOfferDetails() {
    const { offer } = this.props
    const { description } = offer

    if (!description) return null

    return (
      <div className="verso-info-block">
        <h3>
          {'Et en détails ?'}
        </h3>
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
    const { offer, style } = this.props
    const { durationMinutes, extraData, offerType } = offer
    const { author, performer, speaker, stageDirector } = extraData || {}
    const { appLabel } = offerType || {}
    const duration = getDurationFromMinutes(durationMinutes)

    return (
      <div className="verso-info-block">
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
          {durationMinutes && (
            <span>
              {` - Durée ${duration}`}
            </span>
          )}
        </div>
        {style && (
          <div>
            {`Genre : ${style}`}
          </div>
        )}
        {author && (
          <div>
            {`Auteur : ${author}`}
          </div>
        )}
        {performer && (
          <div>
            {`Interprète : ${performer}`}
          </div>
        )}
        {speaker && (
          <div>
            {`Intervenant : ${speaker}`}
          </div>
        )}
        {stageDirector && (
          <div>
            {`Metteur en scène : ${stageDirector}`}
          </div>
        )}
        {offer.id && (
          <DuoOfferContainer
            label="Tu peux réserver deux places."
            offerId={offer.id}
          />
        )}
      </div>
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
        {hasMoreBookables && (
          <li>
            {'Cliquez sur "j’y vais" pour voir plus de dates.'}
          </li>
        )}
      </Fragment>
    )
  }

  renderThingOfferDateInfos() {
    const { bookables } = this.props
    const atLeastOneBookable = bookables.length > 0
    const limitDatetime = atLeastOneBookable ? bookables[0].bookinglimitDatetime : null

    return (
      <li>
        {`Dès maintenant${limitDatetime ? ` et jusqu’au ${limitDatetime}` : ''}`}
      </li>
    )
  }

  renderOfferWhen() {
    const { isBookable, offer } = this.props
    const { isThing } = offer

    const offerDateInfos = isThing
      ? this.renderThingOfferDateInfos()
      : this.renderEventOfferDateInfos()

    return (
      <div className="verso-info-block">
        <h3>
          {'Quand ?'}
        </h3>
        <ul className="dates-info">
          {!isBookable ? (
            <li>
              {'L’offre n’est plus disponible.'}
            </li>
          ) : offerDateInfos}
        </ul>
      </div>
    )
  }

  renderOfferWhere() {
    const { distance, offer, userGeolocation } = this.props
    const { venue } = offer
    const { address, city, latitude, longitude, name, postalCode, publicName } = venue || {}
    const isNotDigitalOffer = latitude && longitude

    return (
      <div className="verso-info-block">
        <div className="flex-columns flex-between">
          <h3>
            {'Où ?'}
          </h3>
          {isNotDigitalOffer && distance && (
            <span className="vco-distance">
              <Icon
                className="vco-geolocation-icon"
                svg="ico-geoloc"
              />
              <span>
                {`À ${distance}`}
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
      </div>
    )
  }

  renderOfferWithdraw() {
    const {
      offer: { withdrawalDetails },
    } = this.props

    return withdrawalDetails ? (
      <div className="verso-info-block">
        <h3>
          {'Modalités de retrait'}
        </h3>
        <div>
          {withdrawalDetails}
        </div>
      </div>
    ) : (
      false
    )
  }

  render() {
    const { isCancelled, booking } = this.props

    return (
      <div className="verso-info">
        {isCancelled === false && booking.completedUrl && (
          <VersoActionsBar url={booking.completedUrl} />
        )}
        {this.renderOfferWhat()}
        {this.renderOfferDetails()}
        {this.renderOfferWhen()}
        {this.renderOfferWhere()}
        {this.renderOfferWithdraw()}
      </div>
    )
  }
}

VersoContentOffer.defaultProps = {
  booking: {},
  distance: null,
  isBookable: true,
  isCancelled: true,
  maxShownDates: 7,
  offer: {},
  style: '',
}

VersoContentOffer.propTypes = {
  bookables: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  booking: PropTypes.shape({
    completedUrl: PropTypes.string,
  }),
  distance: PropTypes.string,
  handleRequestMusicAndShowTypes: PropTypes.func.isRequired,
  isBookable: PropTypes.bool,
  isCancelled: PropTypes.bool,
  maxShownDates: PropTypes.number,
  offer: PropTypes.shape({
    durationMinutes: PropTypes.number,
    description: PropTypes.string,
    id: PropTypes.string,
    isThing: PropTypes.bool,
    venue: PropTypes.shape(),
    product: PropTypes.shape(),
    url: PropTypes.string,
    extraData: PropTypes.shape({
      author: PropTypes.string,
      performer: PropTypes.string,
      speaker: PropTypes.string,
      stageDirector: PropTypes.string,
    }),
    offerType: PropTypes.shape({ appLabel: PropTypes.string }),
    withdrawalDetails: PropTypes.string,
  }),
  style: PropTypes.string,
  userGeolocation: PropTypes.shape().isRequired,
}

export default VersoContentOffer
