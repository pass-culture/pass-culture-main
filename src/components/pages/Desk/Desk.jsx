import PropTypes from 'prop-types'
import React, { Component } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import Main from 'components/layout/Main'
import Titles from 'components/layout/Titles/Titles'
import { formatLocalTimeDateString } from 'utils/timezone'

const TOKEN_MAX_LENGTH = 6
const TOKEN_SYNTAX_VALID = /[^a-z0-9]/i

const CHAR_REMAINING = 'CHAR_REMAINING'
const SYNTAX_INVALID = 'SYNTAX_INVALID'
const VERIFICATION_IN_PROGRESS = 'VERIFICATION_IN_PROGRESS'
const VERIFICATION_SUCCESS = 'VERIFICATION_SUCCESS'
const VERIFICATION_FAILED = 'VERIFICATION_FAILED'
const REGISTERING_IN_PROGRESS = 'REGISTERING_IN_PROGRESS'
const REGISTERING_SUCCESS = 'REGISTERING_SUCCESS'
const REGISTERING_FAILED = 'REGISTERING_FAILED'

const displayBookingDate = booking =>
  !booking.date
    ? 'Permanent'
    : formatLocalTimeDateString(booking.date, booking.venueDepartementCode)

class Desk extends Component {
  constructor(props) {
    super(props)

    this.state = {
      booking: null,
      status: '',
      token: '',
    }
  }

  isValidToken = event => {
    const { getBooking } = this.props
    const token = event.target.value.toUpperCase()
    const status = this.getStatusFromToken(token)
    this.setState({ booking: null, status, token })

    if (status === VERIFICATION_IN_PROGRESS) {
      getBooking(token)
        .then(booking => {
          this.setState({
            booking,
            status: VERIFICATION_SUCCESS,
          })
        })
        .catch(error => {
          error.json().then(body => {
            this.setState({
              status: VERIFICATION_FAILED,
              message: body[Object.keys(body)[0]],
            })
          })
        })
    }
  }

  getStatusFromToken = token => {
    if (token === '') {
      return ''
    }

    if (token.match(TOKEN_SYNTAX_VALID) !== null) {
      return SYNTAX_INVALID
    }

    if (token.length < TOKEN_MAX_LENGTH) {
      return CHAR_REMAINING
    }

    return VERIFICATION_IN_PROGRESS
  }

  registrationOfToken = token => event => {
    event.preventDefault()
    const { validateBooking } = this.props
    this.setState({ status: REGISTERING_IN_PROGRESS })

    validateBooking(token)
      .then(() => {
        const { trackValidateBookingSuccess } = this.props
        this.setState({ status: REGISTERING_SUCCESS })
        trackValidateBookingSuccess(token)
      })
      .catch(error => {
        error.json().then(body => {
          this.setState({
            status: REGISTERING_FAILED,
            message: body[Object.keys(body)[0]],
          })
        })
      })
  }

  getValuesFromStatus = status => {
    let { message, token } = this.state
    let level = ''

    switch (status) {
      case CHAR_REMAINING:
        message = `Caractères restants : ${TOKEN_MAX_LENGTH - token.length}/${TOKEN_MAX_LENGTH}`
        break
      case SYNTAX_INVALID:
        message = 'Caractères valides : de A à Z et de 0 à 9'
        level = 'error'
        break
      case VERIFICATION_IN_PROGRESS:
        message = 'Vérification...'
        break
      case VERIFICATION_SUCCESS:
        message = 'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
        break
      case REGISTERING_IN_PROGRESS:
        message = 'Enregistrement en cours...'
        break
      case REGISTERING_SUCCESS:
        message = 'Enregistrement réussi !'
        break
      case VERIFICATION_FAILED:
        level = 'error'
        break
      case REGISTERING_FAILED:
        level = 'error'
        break
      default:
        message = 'Saisissez une contremarque'
    }

    return {
      level,
      message,
    }
  }

  render() {
    const { booking, status, token } = this.state
    const { level, message } = this.getValuesFromStatus(status)

    return (
      <Main name="desk">
        <Titles title="Guichet" />
        <p className="advice">
          {'Enregistrez les contremarques de réservations présentés par les porteurs du pass.'}
        </p>
        <form>
          <TextInput
            label="Contremarque"
            maxLength={TOKEN_MAX_LENGTH}
            name="token"
            onChange={this.isValidToken}
            placeholder="ex : AZE123"
            type="text"
            value={token}
          />

          {booking && (
            <div
              aria-live="polite"
              aria-relevant="all"
              className="booking-summary"
            >
              <div>
                <div className="desk-label">
                  {'Utilisateur : '}
                </div>
                <div className="desk-value">
                  {booking.userName}
                </div>
              </div>
              <div>
                <div className="desk-label">
                  {'Offre : '}
                </div>
                <div className="desk-value">
                  {booking.offerName}
                </div>
              </div>
              <div>
                <div className="desk-label">
                  {'Date de l’offre : '}
                </div>
                <div className="desk-value">
                  {displayBookingDate(booking)}
                </div>
              </div>
              <div>
                <div className="desk-label">
                  {'Prix : '}
                </div>
                <div className="desk-value">
                  {`${booking.price} €`}
                </div>
              </div>
            </div>
          )}

          <div className="desk-button">
            <button
              className="primary-button"
              disabled={status !== VERIFICATION_SUCCESS}
              onClick={this.registrationOfToken(token)}
              type="submit"
            >
              {'Valider la contremarque'}
            </button>
          </div>

          <div
            aria-live="assertive"
            aria-relevant="all"
            className={`desk-message ${level}`}
          >
            {message}
          </div>
        </form>
      </Main>
    )
  }
}

Desk.propTypes = {
  getBooking: PropTypes.func.isRequired,
  trackValidateBookingSuccess: PropTypes.func.isRequired,
  validateBooking: PropTypes.func.isRequired,
}

export default Desk
