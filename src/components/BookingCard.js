/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { bindActionCreators } from 'redux'
import { requestData } from 'pass-culture-shared'
import currentRecommendationSelector from '../selectors/currentRecommendation'

import submitForm from './forms/submitForm'
import BookingForm from './forms/BookingForm'
import BookingUserUndefined from './BookingUserUndefined'

const renderStepLoading = () => (
  <div className="loading">
    <span>Réservation en cours...</span>
  </div>
)

const renderBookedFooter = () => (
  <p>
    Retrouvez ce code et les détails de l&apos;offre dans la rubrique{' '}
    <Link to="/reservations">Mes Réservations</Link>
    de votre compte
  </p>
)

const renderStepThingBooked = () => (
  <div className="booked thing">
    <h3>
      <span>Votre pouvez accéder à cette offfre à tout moment.</span>
    </h3>
    <p>
      <b>Accéder au cours en ligne</b>
    </p>
    {renderBookedFooter()}
  </div>
)

const renderStepEventBooked = () => {
  const price = '8€'
  const gratuit = false
  return (
    <div className="booked event">
      <h3>
        <span>Votre réservation est validée</span>
      </h3>
      <p>
        {!gratuit && (
          <span className="is-block">
            {price} ont été déduit de votre pass.
          </span>
        )}
        <span className="is-block">Présentez le code suivant sur place:</span>
      </p>
      <p>
        <b>A684P6</b>
      </p>
      {renderBookedFooter()}
    </div>
  )
}

class BookingCard extends React.PureComponent {
  constructor(props) {
    super(props)
    this.formId = 'form-create-booking'
    const actions = { requestData }
    this.actions = bindActionCreators(actions, props.dispatch)
    this.state = {
      canSubmitForm: false,
      isBooked: false,
      isErrored: false,
      isSubmitting: false,
    }
  }

  onFormMutation = ({ invalid, pristine }) => {
    const canSubmitForm = !pristine && !invalid
    this.setState({ canSubmitForm })
  }

  onFormSubmit = values => {
    const onSubmittingStateChanged = () => {
      console.log('BookingCard.onFormSubmit => values', values)
      setTimeout(this.handleRequestSuccess, 3000)
      const { recommendation } = this.props
      console.log('recommendation', recommendation)
      // const body = {
      //   offerId:
      //   quantity: values.quantity,
      //   currentRecommendationId: recommendation.id,
      // }
      // this.actions.requestData('POST', 'bookings', {
      //   body,
      //   name: 'booking',
      //   handleFail: this.handleRequestFail,
      //   handleSuccess: this.handleRequestSuccess,
      // })
    }
    this.setState({ isSubmitting: true }, onSubmittingStateChanged)
  }

  // handleRequestSuccess = (state, action) => {}
  handleRequestSuccess = () => {
    const nextState = { isBooked: true, isErrored: false, isSubmitting: false }
    this.setState(nextState)
  }

  handleRequestFail = () => {
    const nextState = { isBooked: false, isErrored: true, isSubmitting: false }
    this.setState(nextState)
  }

  cancelBookingHandler = () => {
    const { match, history } = this.props
    const baseurl = match.url.replace('/booking', '')
    history.replace(baseurl)
  }

  renderFormControls = () => {
    const { isBooked, isSubmitting, canSubmitForm } = this.state
    const showOkButton = isBooked
    const showCancelButton = !isSubmitting && !isBooked
    const showSubmitButton = showCancelButton && canSubmitForm
    return (
      <React.Fragment>
        {showCancelButton && (
          <button
            type="reset"
            className="has-text-centered my5"
            onClick={this.cancelBookingHandler}
          >
            <span>Annuler</span>
          </button>
        )}
        {showSubmitButton && (
          <button
            type="submit"
            className="has-text-centered my5"
            onClick={() => submitForm(this.formId)}
          >
            <b>Valider</b>
          </button>
        )}
        {showOkButton && (
          <button
            type="button"
            className="has-text-centered my5"
            onClick={this.cancelBookingHandler}
          >
            <b>OK</b>
          </button>
        )}
      </React.Fragment>
    )
  }

  render() {
    const initialValues = { quantity: 1 }
    const { recommendation } = this.props
    const { isBooked, isErrored, isSubmitting } = this.state
    const isEvent = false
    const userConnected = false
    const showForm = !isSubmitting && !isBooked && !isErrored
    return (
      <div id="booking-card" className="is-overlay flex-rows">
        <header className="flex-0">
          <h1 className="title">
            <span>{get(recommendation, 'offer.eventOrThing.name')}</span>
          </h1>
          <h2 className="subtitle">
            <span>{get(recommendation, 'offer.venue.name')}</span>
          </h2>
        </header>
        <div className="main flex-1 items-center is-clipped is-relative">
          <div className="views-container is-overlay">
            {isSubmitting && renderStepLoading()}
            {isBooked && isEvent && renderStepEventBooked()}
            {isBooked && !isEvent && renderStepThingBooked()}
            {isErrored && <div>Form Submit Error</div>}
            {showForm && (
              <React.Fragment>
                <BookingUserUndefined show={userConnected} />
                <BookingForm
                  id={this.formId}
                  item={recommendation}
                  disabled={userConnected}
                  onSubmit={this.onFormSubmit}
                  initialValues={initialValues}
                  onMutation={this.onFormMutation}
                  onValidation={this.onFormValidation}
                />
              </React.Fragment>
            )}
          </div>
        </div>
        <div className="form-footer flex-columns flex-0 flex-center">
          {this.renderFormControls()}
        </div>
      </div>
    )
  }
}

BookingCard.defaultProps = {
  recommendation: null,
}

BookingCard.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  recommendation: PropTypes.object,
}

const mapStateToProps = (state, { match: { params } }) => ({
  recommendation: currentRecommendationSelector(
    state,
    params.offerId,
    params.mediationId
  ),
})

export default connect(mapStateToProps)(BookingCard)
