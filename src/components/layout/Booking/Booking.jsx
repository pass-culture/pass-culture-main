import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Transition } from 'react-transition-group'

import BookingForm from './BookingForm/BookingForm'
import BookingError from './BookingError/BookingError'
import BookingLoader from './BookingLoader/BookingLoader'
import BookingHeader from './BookingHeader/BookingHeader'
import BookingSuccess from './BookingSuccess/BookingSuccess'
import externalSubmitForm from '../../forms/utils/externalSubmitForm'
import { priceIsDefined } from '../../../helpers/getDisplayPrice'
import getIsBooking from '../../../helpers/getIsBooking'
import { ROOT_PATH } from '../../../utils/config'
import handleRedirect from './utils/handleRedirect'

const BOOKING_FORM_ID = 'form-create-booking'

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`

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
    const { handleSubmit } = this.props
    const { isDuo } = formValues
    const quantity = isDuo ? 2 : 1
    const payload = { ...formValues, quantity }
    this.setState(
      { isSubmitting: true },
      handleSubmit(payload, this.handleRequestFail, this.handleRequestSuccess)
    )
  }

  handleRequestSuccess = (state, action) => {
    const { trackBookingSuccess } = this.props
    const { payload } = action
    const { datum } = payload
    const nextState = {
      bookedPayload: datum,
      isErrored: false,
      isSubmitting: false,
    }
    trackBookingSuccess()
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
    const { history, match } = this.props
    const { bookedPayload } = this.state
    const nextUrl = handleRedirect(bookedPayload, match)
    history.replace(nextUrl)
  }

  renderFormControls = () => {
    const { canSubmitForm, bookedPayload, isSubmitting, isErrored } = this.state

    const showCancelButton = !isSubmitting && !bookedPayload
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
            <span>
              {'Annuler'}
            </span>
          </button>
        )}

        {showSubmitButton && (
          <button
            className="has-text-centered my5"
            id="booking-validation-button"
            onClick={externalSubmitForm(BOOKING_FORM_ID)}
            type="submit"
          >
            <b>
              {'Valider'}
            </b>
          </button>
        )}

        {bookedPayload && (
          <button
            className="text-center my5"
            id="booking-success-ok-button"
            onClick={this.handleReturnToDetails}
            type="button"
          >
            <b>
              {'OK'}
            </b>
          </button>
        )}
      </Fragment>
    )
  }

  render() {
    const { bookables, extraClassName, match, offer, recommendation } = this.props

    const isBooking = getIsBooking(match)

    if (!isBooking) {
      return null
    }

    const { canSubmitForm, errors, bookedPayload, isErrored, isSubmitting, mounted } = this.state
    const { id: recommendationId } = recommendation || {}
    const { isEvent, id: offerId } = offer || {}
    const defaultBookable = bookables && bookables[0]
    const showForm = defaultBookable && !bookedPayload && !isErrored && !isSubmitting

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
            className={`is-overlay is-clipped flex-rows ${extraClassName} ${state}`}
            id="booking-card"
          >
            <div className="main flex-rows flex-1 scroll-y">
              <BookingHeader offer={offer} />
              <div
                className="content flex-1 flex-center items-center"
                style={{ backgroundImage }}
              >
                <div className="py36 px12 flex-rows">
                  {isSubmitting && <BookingLoader />}

                  {bookedPayload && (
                    <BookingSuccess
                      bookedPayload={bookedPayload}
                      isEvent={isEvent}
                    />
                  )}

                  {isErrored && <BookingError errors={errors} />}

                  {showForm && (
                    <BookingForm
                      canSubmitForm={canSubmitForm}
                      className="flex-1 flex-rows flex-center items-center"
                      formId={BOOKING_FORM_ID}
                      initialValues={formInitialValues}
                      isEvent={isEvent}
                      isReadOnly={isReadOnly}
                      offerId={offerId}
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
  extraClassName: '',
  offer: null,
  recommendation: null,
}

Booking.propTypes = {
  bookables: PropTypes.arrayOf(PropTypes.shape()),
  extraClassName: PropTypes.string,
  handleSubmit: PropTypes.func.isRequired,
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
    id: PropTypes.string,
  }),
  recommendation: PropTypes.shape({
    id: PropTypes.string,
  }),
  trackBookingSuccess: PropTypes.func.isRequired,
}

export default Booking
