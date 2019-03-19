/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { connect } from 'react-redux'
import { Transition } from 'react-transition-group'
import { bindActionCreators } from 'redux'
import { requestData } from 'redux-saga-data'
import { resolveCurrentUser } from 'with-login'

import { externalSubmitForm } from '../forms/utils'
import BookingCancel from './BookingCancel'
import BookingForm from './BookingForm'
import BookingError from './BookingError'
import BookingLoader from './BookingLoader'
import BookingHeader from './BookingHeader'
import BookingSuccess from './BookingSuccess'
import { priceIsDefined } from '../../helpers/getPrice'
import { selectBookables } from '../../selectors/selectBookables'
import { selectBookingById } from '../../selectors/selectBookings'
import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { ROOT_PATH } from '../../utils/config'

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

class Booking extends PureComponent {
  constructor(props) {
    super(props)
    this.formId = 'form-create-booking'
    const actions = { requestData }
    this.actions = bindActionCreators(actions, props.dispatch)
    this.state = {
      bookedPayload: false,
      canSubmitForm: false,
      errors: null,
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
      this.actions.requestData({
        apiPath: '/bookings',
        // NOTE -> pas de gestion de stock
        // valeur des quantites a 1 par defaut pour les besoins API
        body: { ...formValues, quantity: 1 },
        handleFail: this.handleRequestFail,
        // après la mise à jour du booking pour un user
        // on cherche à recupérer la nouvelle valeur du wallet
        // il faut alors une nouvelle requête pour l'update du store redux
        handleSuccess: this.updateUserFromStore,
        method: 'POST',
        name: 'booking',
      })
    }
    // appel au service apres le changement du state
    this.setState({ isSubmitting: true }, onSubmittingStateChanged)
  }

  updateUserFromStore = (state, action) => {
    const { payload } = action
    const bookedPayload = payload.datum
    this.actions.requestData({
      apiPath: '/users/current',
      body: {},
      handleFail: this.handleRequestFail,
      handleSuccess: this.handleRequestSuccess(bookedPayload),
      method: 'PATCH',
      // IMPORTANT: this resolve is important to keep
      // track the currentUser with the
      // selectCurrentUser selector
      resolve: resolveCurrentUser,
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
    const {
      payload: { errors },
    } = action
    const isErrored = errors && Object.keys(errors).length > 0
    const nextState = {
      bookedPayload: false,
      errors,
      isErrored,
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
      <Fragment>
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
      </Fragment>
    )
  }

  render() {
    const userConnected = false
    const {
      bookables,
      booking,
      extraClassName,
      isCancelled,
      isEvent,
      recommendation,
    } = this.props

    const {
      bookedPayload,
      errors,
      isErrored,
      isSubmitting,
      mounted,
    } = this.state
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
      recommendationId: recommendation && recommendation.id,
      stockId: (defaultBookable && defaultBookable.id) || null,
    }
    return (
      <Transition in={mounted} timeout={0}>
        {state => (
          <div
            id="booking-card"
            className={classnames(
              'is-overlay is-clipped flex-rows',
              extraClassName
            )}
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <div className="main flex-rows flex-1 scroll-y">
              <BookingHeader recommendation={recommendation} />
              <div
                className="content flex-1 flex-center items-center"
                style={{ backgroundImage }}
              >
                <div className="py36 px12 flex-rows">
                  {isSubmitting && <BookingLoader />}
                  {bookedPayload && (
                    <BookingSuccess isEvent={isEvent} data={bookedPayload} />
                  )}
                  {isCancelled && (
                    <BookingCancel isEvent={isEvent} data={booking} />
                  )}
                  {isErrored && <BookingError errors={errors} />}
                  {showForm && (
                    <BookingForm
                      className="flex-1 flex-rows flex-center items-center"
                      formId={this.formId}
                      initialValues={formInitialValues}
                      isEvent={isEvent}
                      isReadOnly={isReadOnly}
                      disabled={userConnected}
                      onSubmit={this.onFormSubmit}
                      onMutation={this.onFormMutation}
                      onValidation={this.onFormValidation}
                    />
                  )}
                </div>
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
  booking: null,
  extraClassName: null,
  isCancelled: false,
  isEvent: false,
  recommendation: null,
}

Booking.propTypes = {
  bookables: PropTypes.array,
  booking: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  extraClassName: PropTypes.string,
  history: PropTypes.object.isRequired,
  isCancelled: PropTypes.bool,
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
  const isEvent = (get(recommendation, 'offer.eventId') && true) || false
  const bookables = selectBookables(state, recommendation, match)
  const booking = selectBookingById(state, bookingId)

  return {
    bookables,
    booking,
    isCancelled: view === 'cancelled',
    isEvent,
    recommendation,
  }
}

export default connect(mapStateToProps)(Booking)
