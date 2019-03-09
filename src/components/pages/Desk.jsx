import {
  getRequestErrorStringFromErrors,
  Icon,
  withLogin,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import Main from '../layout/Main'
import { formatLocalTimeDateString } from '../../utils/timezone'

// Configurable
const CONFIG_CODE_LENGTH = 6
const CONFIG_BAD_CODE_REGEX = /[^a-z0-9]/i

// Component states
const DESK_WAIT = 'DESK_WAIT'
const DESK_TYPE = 'DESK_TYPE'
const DESK_INVALID = 'DESK_INVALID'
const DESK_GET_VERIFICATION = 'DESK_GET_VERIFICATION'
const DESK_RECEIVE_VERIFICATION_USED = 'DESK_RECEIVE_VERIFICATION_USED'
const DESK_RECEIVE_VERIFICATION_NOT_USED = 'DESK_RECEIVE_VERIFICATION_NOT_USED'
const DESK_FAIL_VERIFICATION = 'DESK_FAIL_VERIFICATION'
const DESK_POST_REGISTER = 'DESK_POST_REGISTER'
const DESK_RECEIVE_REGISTER = 'DESK_RECEIVE_REGISTER'
const DESK_FAIL_REGISTER = 'DESK_FAIL_REGISTER'

const DEFAULT_STATE = { name: DESK_WAIT, code: '', booking: null }

const displayBookingDate = booking => {
  if (!booking) {
    return null
  }

  if (booking.date) {
    return formatLocalTimeDateString(booking.date, booking.venueDepartementCode)
  }

  return 'Permanent'
}

const DeskState = ({ message, level, booking }) => (
  <div className="desk-state">
    <table className="booking-summary">
      <tbody>
        <tr>
          <th>Utilisateur :</th>
          <td>{booking && booking.userName}</td>
        </tr>
        <tr>
          <th>Offre :</th>
          <td>{booking && booking.offerName}</td>
        </tr>
        <tr>
          <th>Date de l'offre :</th>
          <td>{displayBookingDate(booking)}</td>
        </tr>
      </tbody>
    </table>
    <div className={`state ${level}`}>
      {level === 'success' && <Icon svg="picto-validation" />}
      {level === 'error' && <Icon svg="picto-echec" />}
      <span>{message}</span>
    </div>
  </div>
)

DeskState.defaultProps = {
  level: 'pending',
}

DeskState.propTypes = {
  message: PropTypes.string.isRequired,
  level: PropTypes.string,
  booking: PropTypes.object,
}

class Desk extends Component {
  constructor(props) {
    super(props)
    this.state = DEFAULT_STATE
  }

  getBookingDataFor = code => {
    const { dispatch } = this.props
    dispatch(
      requestData({
        apiPath: `/bookings/token/${code}`,
        handleSuccess: (state, action) => {
          const { payload } = action
          const booking = payload.datum
          if (booking.isValidated === true) {
            this.setState({ name: DESK_RECEIVE_VERIFICATION_USED })
          } else {
            this.setState({ name: DESK_RECEIVE_VERIFICATION_NOT_USED })
          }
          this.setState({ booking })
        },
        handleFail: (state, action) => {
          const {
            payload: { errors },
          } = action
          this.setState({
            name: DESK_FAIL_VERIFICATION,
            message: getRequestErrorStringFromErrors(errors),
          })
        },
        stateKey: 'deskBookings',
      })
    )
  }

  postRegistrationFor = code => {
    const { dispatch } = this.props
    dispatch(
      requestData({
        apiPath: `/bookings/token/${code}`,
        handleSuccess: () => {
          this.setState({ name: DESK_RECEIVE_REGISTER })
        },
        handleFail: (state, action) => {
          const {
            payload: { errors },
          } = action
          this.setState({
            name: DESK_FAIL_REGISTER,
            message: getRequestErrorStringFromErrors(errors),
          })
        },
        method: 'PATCH',
      })
    )
  }

  handleCodeChange = event => {
    const code = event.target.value.toUpperCase()
    this.setState({ code })

    if (code === '') {
      return this.setState({ name: DESK_WAIT })
    }

    if (code.match(CONFIG_BAD_CODE_REGEX) !== null) {
      return this.setState({ name: DESK_INVALID })
    }

    if (code.length < CONFIG_CODE_LENGTH) {
      return this.setState({ name: DESK_TYPE })
    }

    this.setState({ name: DESK_GET_VERIFICATION })
    return this.getBookingDataFor(code)
  }

  handleCodeRegistration = code => {
    this.setState({ name: DESK_POST_REGISTER, code: '' })
    this.postRegistrationFor(code)
    this.input.focus()
  }

  componentDidMount() {
    this.input.focus()
  }

  render() {
    return (
      <Main name="desk">
        <div className="section hero">
          <h1 className="main-title">Guichet</h1>
          <p className="subtitle">
            Enregistrez les codes de réservations présentés par les porteurs du
            Pass.
          </p>
        </div>

        <div className="section form">
          <p className="subtitle is-medium has-text-weight-bold">
            Scannez un code-barres, ou saisissez-le ci-dessous:
          </p>

          <input
            className="input is-undefined"
            type="text"
            ref={element => (this.input = element)}
            name="code"
            onChange={this.handleCodeChange.bind(this)}
            maxLength={CONFIG_CODE_LENGTH}
            value={this.state.code}
          />

          <button
            disabled={this.state.name !== DESK_RECEIVE_VERIFICATION_NOT_USED}
            className="button"
            type="submit"
            onClick={() => this.handleCodeRegistration(this.state.code)}>
            Valider
          </button>

          {this.state.name === DESK_WAIT && (
            <DeskState message="Saisissez un code" />
          )}

          {this.state.name === DESK_TYPE && (
            <DeskState
              message={`caractères restants: ${CONFIG_CODE_LENGTH -
                this.state.code.length}/${CONFIG_CODE_LENGTH}`}
            />
          )}

          {this.state.name === DESK_INVALID && (
            <DeskState
              level="error"
              message="Caractères valides : de A à Z et de 0 à 9"
            />
          )}

          {this.state.name === DESK_GET_VERIFICATION && (
            <DeskState message="Vérification..." />
          )}

          {this.state.name === DESK_RECEIVE_VERIFICATION_USED && (
            <DeskState
              booking={this.state.booking}
              message="Ce coupon est déjà enregistré"
              level="error"
            />
          )}

          {this.state.name === DESK_RECEIVE_VERIFICATION_NOT_USED && (
            <DeskState
              booking={this.state.booking}
              message="Coupon vérifié, cliquez sur OK pour enregistrer"
            />
          )}

          {this.state.name === DESK_POST_REGISTER && (
            <DeskState
              booking={this.state.booking}
              message="Enregistrement en cours..."
            />
          )}

          {this.state.name === DESK_RECEIVE_REGISTER && (
            <DeskState
              booking={this.state.booking}
              message="Enregistrement réussi!"
              level="success"
            />
          )}

          {(this.state.name === DESK_FAIL_VERIFICATION ||
            this.state.name === DESK_FAIL_REGISTER) && (
            <DeskState
              booking={this.state.booking}
              level="error"
              message={this.state.message}
            />
          )}

          <NavLink
            id="exitlink"
            className="button is-primary is-medium is-pulled-right"
            to="/accueil">
            Terminer
          </NavLink>
        </div>
      </Main>
    )
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect()
)(Desk)
