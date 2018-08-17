/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { requestData } from 'pass-culture-shared'
import currentRecommendationSelector from '../selectors/currentRecommendation'

import BookingForm from './forms/BookingForm'
import BookingUserUndefined from './booking/BookingUserUndefined'

class BookingCard extends React.PureComponent {
  constructor(props) {
    super(props)
    this.formId = 'form-create-booking'
    this.state = { isvalid: false, pristine: true }
    const actions = { requestData }
    this.actions = bindActionCreators(actions, props.dispatch)
  }

  onFormMutation = ({ pristine }) => {
    this.setState({ pristine })
  }

  onFormValidation = args => {
    const { values, errors } = args
    const haserrors =
      values &&
      (errors !== null || errors !== undefined) &&
      Object.keys(errors).length > 0
    this.setState({ isvalid: !haserrors })
  }

  onFormSubmit = values => {
    console.log('BookingCard ---> onFormSubmit')
    console.log('values', values)
    const { recommendation } = this.props
    console.log('recommendation', recommendation)
    // const body = {
    //   quantity: 1,
    //   offerId:
    //   currentRecommendationId:
    // }
    // this.actions.requestData('POST', 'bookings', {
    //   body,
    //   name: 'booking',
    // })
  }

  cancelButtonHandler = () => {
    const event = new Event('submit')
    document.getElementById(this.formId).dispatchEvent(event)
  }

  cancelButtonClick = () => {
    const { match, history } = this.props
    const baseurl = match.url.replace('/booking', '')
    history.replace(baseurl)
  }

  submitButtonClick = () => {
    // NOTE -> soumission du form depuis un element exterieur au form
    const event = new Event('submit')
    document.getElementById(this.formId).dispatchEvent(event)
  }

  render() {
    const { isvalid, pristine } = this.state
    const { recommendation } = this.props
    const showAlert = false
    const canSubmit = isvalid && !pristine
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
        <div className="main flex-1 items-center">
          <BookingUserUndefined show={showAlert} />
          <BookingForm
            id={this.formId}
            item={recommendation}
            onSubmit={this.onFormSubmit}
            onMutation={this.onFormMutation}
            onValidation={this.onFormValidation}
            className="flex-rows items-center has-text-centered"
          />
        </div>
        <div className="form-footer flex-columns flex-0 items-center has-text-centered">
          <button type="reset" onClick={this.cancelButtonClick}>
            <span>Annuler</span>
          </button>
          {canSubmit && (
            <button type="submit" onClick={this.submitButtonClick}>
              <b>Valider</b>
            </button>
          )}
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
