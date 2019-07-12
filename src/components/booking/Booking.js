import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Transition } from 'react-transition-group'
import { bindActionCreators } from 'redux'
import { requestData } from 'redux-saga-data'
import { resolveCurrentUser } from 'with-react-redux-login'

import { externalSubmitForm } from '../forms/utils'
import BookingCancel from './sub-items/BookingCancel'
import BookingForm from './sub-items/BookingForm'
import BookingError from './sub-items/BookingError'
import BookingLoader from './sub-items/BookingLoader'
import BookingHeader from './sub-items/BookingHeader'
import BookingSuccess from './sub-items/BookingSuccess'
import { priceIsDefined } from '../../helpers/getDisplayPrice'
import { ROOT_PATH } from '../../utils/config'
import { showCardDetails } from '../../reducers/card'

const BOOKING_FORM_ID = 'form-create-booking'

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

  handleOnFormMutation = ({ invalid, values }) => {
    const nextCanSubmitForm = Boolean(!invalid && values.stockId && values.price >= 0)
    this.setState({ canSubmitForm: nextCanSubmitForm })
  }

  handleOnFormSubmit = formValues => {
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
    const bookedPayload = get(action, 'payload.datum')
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

  handleCancelBookingHandler = () => {
    const { match, history } = this.props
    const baseUrl = match.url.replace('/booking', '')
    history.replace(baseUrl)
  }

  handleGetBackToOffer = () => {
    const { dispatch, history, match } = this.props
    const offerId = get(match.params, 'offerId')
    const url = `/decouverte/${offerId}`

    dispatch(
      requestData({
        apiPath: '/users/current',
        method: 'PATCH',
        resolve: resolveCurrentUser,
      })
    )
    dispatch(showCardDetails())

    history.push(url)
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
            className="text-center my5"
            id="booking-close-button"
            onClick={this.handleCancelBookingHandler}
            type="reset"
          >
            <span>{'Annuler'}</span>
          </button>
        )}

        {showSubmitButton && (
          <button
            className="has-text-centered my5"
            id="booking-validation-button"
            onClick={externalSubmitForm(BOOKING_FORM_ID)}
            type="submit"
          >
            <b>{'Valider'}</b>
          </button>
        )}

        {bookedPayload && (
          <button
            className="text-center my5"
            id="booking-success-ok-button"
            onClick={this.handleCancelBookingHandler}
            type="button"
          >
            <b>{'OK'}</b>
          </button>
        )}

        {isCancelled && (
          <button
            className="text-center my5"
            id="booking-cancellation-confirmation-button"
            onClick={this.handleGetBackToOffer}
            type="button"
          >
            <b>{'OK'}</b>
          </button>
        )}
      </Fragment>
    )
  }

  render() {
    const userConnected = false
    const { bookables, booking, extraClassName, isCancelled, isEvent, recommendation } = this.props

    const { bookedPayload, errors, isErrored, isSubmitting, mounted } = this.state

    const showForm = !isSubmitting && !bookedPayload && !isErrored && !isCancelled
    const defaultBookable = !isEvent && get(bookables, '[0]')
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
        defaultBookable && priceIsDefined(defaultBookable.price) ? defaultBookable.price : null,
      recommendationId: recommendation && recommendation.id,
      stockId: (defaultBookable && defaultBookable.id) || null,
    }
    return (
      <Transition
        in={mounted}
        timeout={0}
      >
        {state => (
          <div
            className={classnames('is-overlay is-clipped flex-rows', extraClassName)}
            id="booking-card"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <div className="main flex-rows flex-1 scroll-y">
              <BookingHeader recommendation={recommendation} />
              <div
                className={`content flex-1 flex-center ${isCancelled ? '' : 'items-center'}`}
                style={{ backgroundImage }}
              >
                <div className={`${isCancelled ? '' : 'py36 px12'} flex-rows`}>
                  {isSubmitting && <BookingLoader />}

                  {bookedPayload && <BookingSuccess
                    data={bookedPayload}
                    isEvent={isEvent}
                                    />}

                  {isCancelled && <BookingCancel
                    data={booking}
                    isEvent={isEvent}
                                  />}

                  {isErrored && <BookingError errors={errors} />}

                  {showForm && (
                    <BookingForm
                      className="flex-1 flex-rows flex-center items-center"
                      disabled={userConnected}
                      formId={BOOKING_FORM_ID}
                      initialValues={formInitialValues}
                      isEvent={isEvent}
                      isReadOnly={isReadOnly}
                      onMutation={this.handleOnFormMutation}
                      onSubmit={this.handleOnFormSubmit}
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
  bookables: PropTypes.arrayOf(PropTypes.shape()),
  booking: PropTypes.shape(),
  dispatch: PropTypes.func.isRequired,
  extraClassName: PropTypes.string,
  history: PropTypes.shape().isRequired,
  isCancelled: PropTypes.bool,
  isEvent: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  match: PropTypes.shape().isRequired,
  recommendation: PropTypes.shape(),
}

export default Booking
