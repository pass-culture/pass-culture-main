import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { capitalize } from 'react-final-form-utils'

import { navigationLink } from '../../../../../utils/geolocation'
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
    const limitDatetime = get(bookables, '[0].bookinglimitDatetime')

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
    const { distance, offer } = this.props
    const { venue } = offer || {}
    const { address, city, latitude, longitude, name, postalCode, publicName } = venue || {}

    return (
      <Fragment>
        <div className="flex-columns flex-between">
          <h3>
            {'Où ?'}
          </h3>
          {latitude && longitude && (
            <a
              className="distance"
              href={navigationLink(latitude, longitude)}
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon
                alt="Géolocalisation dans Open Street Map"
                className="geolocation-icon"
                png="geoloc"
              />
              <span>
                {`À ${distance}`}
              </span>
            </a>
          )}
        </div>
        <address>
          {publicName || name}
          <br />
          {address && address}
          <br />
          {postalCode && postalCode}
          <br />
          {city && city}
          <br />
        </address>
        {latitude && longitude && (
          <a
            className="itinerary"
            href={navigationLink(latitude, longitude)}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon
              alt="Géolocalisation dans Open Street Map"
              className="geolocation-icon"
              png="go"
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
  style: '',
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
    product: PropTypes.shape(),
  }),
  style: PropTypes.string,
}

export default VersoContentOffer
