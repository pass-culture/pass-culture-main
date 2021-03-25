import PropTypes from 'prop-types'
import React, { Component } from 'react'

import AppLayout from 'app/AppLayout'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { formatLocalTimeDateString } from 'utils/timezone'

class Desk extends Component {
  constructor(props) {
    super(props)

    this.state = {
      booking: null,
      isDisabledButton: true,
      isUsedToken: false,
      level: '',
      message: 'Saisissez une contremarque',
      token: '',
    }

    this.TOKEN_MAX_LENGTH = 6
    this.VALID_TOKEN_SYNTAX = /[^a-z0-9]/i
    this.BOOKING_ALREADY_USED = 410
  }

  formattedBookingDate = booking =>
    !booking.datetime
      ? 'Permanent'
      : formatLocalTimeDateString(
        booking.datetime,
        booking.venueDepartementCode,
        "dd/MM/yyyy - HH'h'mm"
      )

  firstErrorMessageFromApi = body => Object.keys(body)[0]

  validateToken = event => {
    const { getBooking } = this.props
    const token = event.target.value.toUpperCase()
    const { canCheckTheToken, level, message } = this.getStatusFromToken(token)
    this.setState({
      booking: null,
      isDisabledButton: true,
      isUsedToken: false,
      level,
      message,
      token,
    })

    if (canCheckTheToken) {
      getBooking(token)
        .then(booking => {
          this.setState({
            booking,
            isDisabledButton: false,
            message: 'Coupon vérifié, cliquez sur "Valider" pour enregistrer',
          })
        })
        .catch(error => {
          if (error.status === this.BOOKING_ALREADY_USED) {
            error.json().then(body => {
              this.setState({
                level: '',
                isUsedToken: true,
                message: body[this.firstErrorMessageFromApi(body)],
              })
            })
          } else {
            error.json().then(body => {
              this.setState({
                level: 'error',
                message: body[this.firstErrorMessageFromApi(body)],
              })
            })
          }
        })
    }
  }

  getStatusFromToken = token => {
    if (token === '') {
      return {
        canCheckTheToken: false,
        level: '',
        message: 'Saisissez une contremarque',
      }
    }

    if (token.match(this.VALID_TOKEN_SYNTAX) !== null) {
      return {
        canCheckTheToken: false,
        level: 'error',
        message: 'Caractères valides : de A à Z et de 0 à 9',
      }
    }

    if (token.length < this.TOKEN_MAX_LENGTH) {
      return {
        canCheckTheToken: false,
        level: '',
        message: `Caractères restants : ${this.TOKEN_MAX_LENGTH - token.length}/${
          this.TOKEN_MAX_LENGTH
        }`,
      }
    }

    return {
      canCheckTheToken: true,
      level: '',
      message: 'Vérification...',
    }
  }

  registrationOfToken = token => event => {
    event.preventDefault()
    const { validateBooking } = this.props
    this.setState({
      message: 'Validation en cours...',
    })

    validateBooking(token)
      .then(() => {
        const { trackValidateBookingSuccess } = this.props
        this.setState({
          message: 'Contremarque validée !',
        })
        trackValidateBookingSuccess(token)
      })
      .then(() => {
        this.setState({
          isDisabledButton: false,
          isUsedToken: true,
        })
      })
      .catch(error => {
        error.json().then(body => {
          this.setState({
            level: 'error',
            message: body[this.firstErrorMessageFromApi(body)],
          })
        })
      })
  }

  invalidationOfToken = token => event => {
    event.preventDefault()
    const { invalidateBooking } = this.props
    this.setState({
      message: 'Invalidation en cours...',
    })

    invalidateBooking(token)
      .then(() => {
        this.setState({
          message: 'Contremarque invalidée !',
        })
      })
      .then(() => {
        this.setState({
          isUsedToken: false,
          isDisabledButton: false,
        })
      })
  }

  render() {
    const { booking, isDisabledButton, isUsedToken, level, message, token } = this.state

    return (
      <AppLayout layoutConfig={{ pageName: 'desk' }}>
        <PageTitle title="Guichet" />
        <Titles title="Guichet" />
        <p className="advice">
          {
            'Saisissez les contremarques présentées par les jeunes afin de les valider ou de les invalider.'
          }
        </p>
        <form>
          <TextInput
            label="Contremarque"
            maxLength={this.TOKEN_MAX_LENGTH}
            name="token"
            onChange={this.validateToken}
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
                  {this.formattedBookingDate(booking)}
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
            {isUsedToken && (
              <button
                className="secondary-button"
                onClick={this.invalidationOfToken(token)}
                type="submit"
              >
                {'Invalider la contremarque'}
              </button>
            )}
            {!isUsedToken && (
              <button
                className="primary-button"
                disabled={isDisabledButton}
                onClick={this.registrationOfToken(token)}
                type="submit"
              >
                {'Valider la contremarque'}
              </button>
            )}
          </div>

          <div
            aria-live="assertive"
            aria-relevant="all"
            className={`desk-message ${level}`}
          >
            {message}
          </div>
        </form>
      </AppLayout>
    )
  }
}

Desk.propTypes = {
  getBooking: PropTypes.func.isRequired,
  invalidateBooking: PropTypes.func.isRequired,
  trackValidateBookingSuccess: PropTypes.func.isRequired,
  validateBooking: PropTypes.func.isRequired,
}

export default Desk
