import classnames from 'classnames'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Transition } from 'react-transition-group'
import { requestData } from 'redux-saga-data'

import BookingCancel from './BookingCancel/BookingCancel'
import BookingForm from './BookingForm/BookingForm'
import BookingError from './BookingError/BookingError'
import BookingLoader from './BookingLoader/BookingLoader'
import BookingHeader from './BookingHeader/BookingHeader'
import BookingSuccess from './BookingSuccess/BookingSuccess'
import { externalSubmitForm } from '../../forms/utils'
import { priceIsDefined } from '../../../helpers/getDisplayPrice'
import getIsBooking from '../../../helpers/getIsBooking'
import getIsConfirmingCancelling from '../../../helpers/getIsConfirmingCancelling'
import { ROOT_PATH } from '../../../utils/config'
import { bookingNormalizer } from '../../../utils/normalizers'

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
    this.handleSetMounted(true)
  }

  componentWillUnmount() {
    this.handleSetMounted(false)
  }

  handleSetMounted = mounted => {
    this.setState({ mounted })
  }

  handleSetCanSubmitForm = canSubmitForm => {
    this.setState({ canSubmitForm })
  }

  handleFormSubmit = formValues => {
    const { dispatch } = this.props
    const onSubmittingStateChanged = () => {
      dispatch(
        requestData({
          apiPath: '/bookings',
          // NOTE -> pas de gestion de stock
          // valeur des quantites a 1 par defaut pour les besoins API
          body: { ...formValues, quantity: 1 },
          handleFail: this.handleRequestFail,
          handleSuccess: this.handleRequestSuccess,
          method: 'POST',
          name: 'booking',
          normalizer: bookingNormalizer,
        })
      )
    }
    // appel au service apres le changement du state
    this.setState({ isSubmitting: true }, onSubmittingStateChanged)
  }

  handleRequestSuccess = (state, action) => {
    const { payload } = action
    const { datum } = payload
    const nextState = {
      bookedPayload: datum,
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

  handleReturnToDetails = () => {
    const { match, history } = this.props
    const { url } = match
    const detailsUrl = url.split(/\/reservation(\/|$|\/$)/)[0]
    history.replace(detailsUrl)
  }

  renderFormControls = () => {
    const { match } = this.props
    const { canSubmitForm, bookedPayload, isSubmitting, isErrored } = this.state

    const isConfirmingCancelling = getIsConfirmingCancelling(match)
    const showCancelButton = !isSubmitting && !bookedPayload && !isConfirmingCancelling
    const showSubmitButton = showCancelButton && canSubmitForm && !isErrored

    return (
      <Fragment>
        {showCancelButton && (
          <button
            className="text-center my5"
            id="booking-close-button"
            onClick={this.handleReturnToDetails}
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
            onClick={this.handleReturnToDetails}
            type="button"
          >
            <b>{'OK'}</b>
          </button>
        )}

        {isConfirmingCancelling && (
          <button
            className="text-center my5"
            id="booking-cancellation-confirmation-button"
            onClick={this.handleReturnToDetails}
            type="button"
          >
            <b>{'OK'}</b>
          </button>
        )}
      </Fragment>
    )
  }

  render() {
    const { bookables, booking, extraClassName, match, offer, recommendation } = this.props

    const isBooking = getIsBooking(match)

    if (!isBooking) {
      return null
    }

    const { canSubmitForm, errors, bookedPayload, isErrored, isSubmitting, mounted } = this.state
    const { id: recommendationId } = recommendation || {}
    const { isEvent } = offer || {}
    const isConfirmingCancelling = getIsConfirmingCancelling(match)
    const defaultBookable = bookables && bookables[0]
    const showForm =
      defaultBookable && !bookedPayload && !isConfirmingCancelling && !isErrored && !isSubmitting

    let date
    let price
    let stockId
    const isReadOnly = bookables.length === 1
    if (defaultBookable && isReadOnly) {
      date = defaultBookable.beginningDatetime && moment(defaultBookable.beginningDatetime)
      price = priceIsDefined(defaultBookable.price) ? defaultBookable.price : null
      stockId = defaultBookable.id
    }

    const formInitialValues = {
      bookables,
      date,
      price,
      recommendationId,
      stockId,
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
              <BookingHeader offer={offer} />
              <div
                className={`content flex-1 flex-center ${
                  isConfirmingCancelling ? '' : 'items-center'
                }`}
                style={{ backgroundImage }}
              >
                <div className={`${isConfirmingCancelling ? '' : 'py36 px12'} flex-rows`}>
                  {isSubmitting && <BookingLoader />}

                  {bookedPayload && (
                    <BookingSuccess
                      bookedPayload={bookedPayload}
                      isEvent={isEvent}
                    />
                  )}

                  {isConfirmingCancelling && <BookingCancel
                    booking={booking}
                    isEvent={isEvent}
                                             />}

                  {isErrored && <BookingError errors={errors} />}

                  {showForm && (
                    <BookingForm
                      canSubmitForm={canSubmitForm}
                      className="flex-1 flex-rows flex-center items-center"
                      formId={BOOKING_FORM_ID}
                      initialValues={formInitialValues}
                      isEvent={isEvent}
                      isReadOnly={isReadOnly}
                      onFormSubmit={this.handleFormSubmit}
                      onSetCanSubmitForm={this.handleSetCanSubmitForm}
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
  offer: null,
  recommendation: null,
}

Booking.propTypes = {
  bookables: PropTypes.arrayOf(PropTypes.shape()),
  booking: PropTypes.shape(),
  dispatch: PropTypes.func.isRequired,
  extraClassName: PropTypes.string,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      bookings: PropTypes.string,
      cancellation: PropTypes.string,
      confirmation: PropTypes.string,
    }),
    url: PropTypes.string.isRequired,
  }).isRequired,
  offer: PropTypes.shape({
    isEvent: PropTypes.bool,
  }),
  recommendation: PropTypes.shape({
    id: PropTypes.string,
  }),
}

export default Booking
