/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { requestData } from 'pass-culture-shared'
import { Transition } from 'react-transition-group'

import { ROOT_PATH } from '../../utils/config'
import { externalSubmitForm } from '../forms/utils'
import BookingCancel from './BookingCancel'
import BookingForm from './BookingForm'
import BookingError from './BookingError'
import BookingLoader from './BookingLoader'
import BookingHeader from './BookingHeader'
import BookingSuccess from './BookingSuccess'
import BookingActivation from './BookingActivation'
import { priceIsDefined } from '../../helpers/getPrice'
import { selectBookables } from '../../selectors/selectBookables'
import { selectBookingById } from '../../selectors/selectBookings'
import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { isUserActivated } from '../../utils/user'

const duration = 250
const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`

const defaultStyle = {
  top: '100%',
  transition: `top ${duration}ms ease-in-out`,
}

const transitionStyles = {
  entered: { top: 0 },
  entering: { top: '100%' },
  exited: { display: 'none', visibility: 'none' },
}

class Booking extends React.PureComponent {
  constructor(props) {
    super(props)
    this.formId = 'form-create-booking'
    const actions = { requestData }
    this.actions = bindActionCreators(actions, props.dispatch)
    this.state = {
      bookedPayload: false,
      canSubmitForm: false,
      isErrored: false,
      isSubmitting: false,
      mounted: false,
    }
  }

  componentDidMount() {
    this.setState({ mounted: true })
  }

  componentWillUnmount() {
    this.setState({ mounted: false })
  }

  onFormMutation = ({ invalid, values }) => {
    const nextCanSubmitForm = Boolean(
      !invalid && values.stockId && values.price >= 0
    )
    this.setState({ canSubmitForm: nextCanSubmitForm })
  }

  onFormSubmit = formValues => {
    const onSubmittingStateChanged = () => {
      this.actions.requestData('POST', 'bookings', {
        // NOTE -> pas de gestion de stock
        // valeur des quantites a 1 par defaut pour les besoins API
        body: { ...formValues, quantity: 1 },
        handleFail: this.handleRequestFail,
        // après la mise à jour du booking pour un user
        // on cherche à recupérer la nouvelle valeur du wallet
        // il faut alors une nouvelle requête pour l'update du store redux
        handleSuccess: this.updateUserFromStore,
        name: 'booking',
      })
    }
    // appel au service apres le changement du state
    this.setState({ isSubmitting: true }, onSubmittingStateChanged)
  }

  updateUserFromStore = (state, action) => {
    const bookedPayload = action.data
    this.actions.requestData('PATCH', 'users/current', {
      body: {},
      handleFail: this.handleRequestFail,
      handleSuccess: this.handleRequestSuccess(bookedPayload),
      key: 'user',
    })
  }

  handleRequestSuccess = bookedPayload => () => {
    const nextState = {
      bookedPayload,
      isErrored: false,
      isSubmitting: false,
    }
    this.setState(nextState)
  }

  handleRequestFail = (state, action) => {
    const nextState = {
      bookedPayload: false,
      isErrored: action,
      isSubmitting: false,
    }
    this.setState(nextState)
  }

  cancelBookingHandler = () => {
    const { match, history } = this.props
    const baseurl = match.url.replace('/booking', '')
    history.replace(baseurl)
  }

  getBackToBookings = () => {
    const { history } = this.props
    history.push('/reservations')
  }

  renderFormControls = () => {
    const { bookedPayload, isSubmitting, canSubmitForm } = this.state
    const { isCancelled } = this.props
    const showCancelButton = !isSubmitting && !bookedPayload && !isCancelled
    const showSubmitButton = showCancelButton && canSubmitForm
    return (
      <React.Fragment>
        {showCancelButton && (
          <button
            type="reset"
            className="text-center my5"
            onClick={this.cancelBookingHandler}
          >
            <span>Annuler</span>
          </button>
        )}
        {showSubmitButton && (
          <button
            type="submit"
            className="has-text-centered my5"
            onClick={() => externalSubmitForm(this.formId)}
          >
            <b>Valider</b>
          </button>
        )}
        {bookedPayload && (
          <button
            type="button"
            className="text-center my5"
            onClick={this.cancelBookingHandler}
          >
            <b>OK</b>
          </button>
        )}
        {isCancelled && (
          <button
            type="button"
            className="text-center my5"
            onClick={this.getBackToBookings}
          >
            <b>OK</b>
          </button>
        )}
      </React.Fragment>
    )
  }

  render() {
    const userConnected = false
    const {
      booking,
      recommendation,
      bookables,
      isActivatedUser,
      isActivationOffer,
      isCancelled,
      isEvent,
    } = this.props
    const { bookedPayload, isErrored, isSubmitting, mounted } = this.state
    const showForm =
      !isSubmitting && !bookedPayload && !isErrored && !isCancelled
    const defaultBookable = !isEvent && get(bookables, '[0]')
    //
    const isReadOnly = isEvent && bookables.length === 1
    let initialDate = null
    if (isReadOnly) {
      initialDate = get(bookables, '0.beginningDatetime')
      initialDate = moment(initialDate)
    }
    const formInitialValues = {
      bookables,
      date: (initialDate && { date: initialDate }) || null,
      price:
        defaultBookable && priceIsDefined(defaultBookable.price)
          ? defaultBookable.price
          : null,
      recommendationId: recommendation.id,
      stockId: (defaultBookable && defaultBookable.id) || null,
    }
    return (
      <Transition in={mounted} timeout={0}>
        {state => (
          <div
            id="booking-card"
            className="is-overlay is-clipped flex-rows"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <BookingHeader recommendation={recommendation} />
            <div
              className="main flex-1 items-center is-clipped is-relative"
              style={{ backgroundImage }}
            >
              <div className="views-container is-overlay">
                {isSubmitting && <BookingLoader />}
                {bookedPayload && (
                  <BookingSuccess isEvent={isEvent} data={bookedPayload} />
                )}
                {isCancelled && (
                  <BookingCancel isEvent={isEvent} data={booking} />
                )}
                {isErrored && <BookingError {...isErrored} />}
                {showForm && (
                  <React.Fragment>
                    {!isActivationOffer && !isActivatedUser && (
                      <BookingActivation />
                    )}
                    {(isActivationOffer || isActivatedUser) && (
                      <BookingForm
                        className="flex-rows items-center"
                        isEvent={isEvent}
                        formId={this.formId}
                        disabled={userConnected}
                        onSubmit={this.onFormSubmit}
                        onMutation={this.onFormMutation}
                        initialValues={formInitialValues}
                        onValidation={this.onFormValidation}
                      />
                    )}
                  </React.Fragment>
                )}
              </div>
            </div>
            <div className="form-footer flex-columns flex-0 flex-center">
              {this.renderFormControls()}
            </div>
          </div>
        )}
      </Transition>
    )
  }
}

Booking.defaultProps = {
  bookables: null,
  isEvent: false,
  recommendation: null,
}

Booking.propTypes = {
  bookables: PropTypes.array,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isEvent: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  match: PropTypes.object.isRequired,
  recommendation: PropTypes.object,
}

const mapStateToProps = (state, { match }) => {
  const { offerId, mediationId, view, bookingId } = match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const { type } = get(recommendation, 'offer.eventOrThing')
  const isActivationOffer = type === 'EventType.ACTIVATION'
  const isActivatedUser = isUserActivated(state.user)
  const isEvent = (get(recommendation, 'offer.eventId') && true) || false
  const bookables = selectBookables(state, recommendation, match)
  const booking = selectBookingById(state, bookingId)

  return {
    bookables,
    booking,
    isActivatedUser,
    isActivationOffer,
    isCancelled: view === 'cancelled',
    isEvent,
    recommendation,
  }
}

export default connect(mapStateToProps)(Booking)
