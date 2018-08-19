/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import pick from 'lodash.pick'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { requestData } from 'pass-culture-shared'
import currentRecommendationSelector from '../selectors/currentRecommendation'

import { ROOT_PATH } from '../utils/config'
import submitForm from './forms/submitForm'
import selectBookables from '../selectors/selectBookables'
import BookingForm from './BookingForm'
import BookingCardError from './BookingCardError'
import BookingCardLoader from './BookingCardLoader'
import BookingCardSuccess from './BookingCardSuccess'
import BookingUserUndefined from './BookingUserUndefined'

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

  onFormMutation = ({ invalid, pristine, values }) => {
    // intervient aux changement sur le form
    // pour les changements sur 'invalid | pristine | values'
    const nextCanSubmitForm =
      !pristine && !invalid && values.stockId && values.price >= 0
    const canSubmitForm = this.state
    const hasFormValid = canSubmitForm !== nextCanSubmitForm
    if (!hasFormValid) return
    this.setState({ canSubmitForm: nextCanSubmitForm })
  }

  onFormSubmit = formValues => {
    const onSubmittingStateChanged = () => {
      console.log('formValues', formValues)
      // console.log('BookingCard.onFormSubmit => formValues', formValues)
      // setTimeout(this.handleRequestSuccess, 3000)
      this.actions.requestData('POST', 'bookings', {
        body: pick(formValues, [
          'price',
          'stockId',
          'quantity',
          'currentRecommendationId',
        ]),
        handleFail: this.handleRequestFail,
        handleSuccess: this.handleRequestSuccess,
        name: 'booking',
      })
    }
    // appel au service apres le changement du state
    this.setState({ isSubmitting: true }, onSubmittingStateChanged)
  }

  handleRequestSuccess = (state, action) => {
    const nextState = { isBooked: true, isErrored: action, isSubmitting: false }
    this.setState(nextState)
  }

  handleRequestFail = (state, action) => {
    // TODO -> ajouter une gestion des erreurs
    const nextState = {
      isBooked: false,
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
    const { recommendation, bookables, isevent } = this.props
    const { isBooked, isErrored, isSubmitting } = this.state
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
        <div
          className="main flex-1 items-center is-clipped is-relative"
          style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
        >
          <div className="views-container is-overlay">
            {isSubmitting && <BookingCardLoader />}
            {isBooked && <BookingCardSuccess isEvent={isevent} />}
            {isErrored && <BookingCardError {...isErrored} />}
            {showForm && (
              <React.Fragment>
                <BookingUserUndefined show={userConnected} />
                <BookingForm
                  formId={this.formId}
                  disabled={userConnected}
                  onSubmit={this.onFormSubmit}
                  recommendation={recommendation}
                  onMutation={this.onFormMutation}
                  onValidation={this.onFormValidation}
                  className="flex-rows items-center"
                  initialValues={{
                    bookables,
                    currentRecommendationId: recommendation.id,
                    date: null,
                    quantity: 1,
                    stockId: null,
                  }}
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
  bookables: null,
  isevent: false,
  recommendation: null,
}

BookingCard.propTypes = {
  bookables: PropTypes.array,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isevent: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  match: PropTypes.object.isRequired,
  recommendation: PropTypes.object,
}

const mapStateToProps = (state, { match }) => {
  const { offerId, mediationId } = match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const isevent = get(recommendation, 'offer.eventId') || false
  // pas sur qu'un selecteur soit pertinent:
  // perfs -> l'user ne reviendra pas sur la page puisqu'il est déjà venu
  // opaque -> oblige a regarder dans un fichier ce qui se passe
  const bookables = selectBookables(state, recommendation, match)
  return {
    bookables,
    isevent,
    recommendation,
  }
}

export default connect(mapStateToProps)(BookingCard)
