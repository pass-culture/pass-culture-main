import PropTypes from 'prop-types'
import React from 'react'
import { getRequestErrorStringFromErrors } from 'pass-culture-shared'
import { Link } from 'react-router-dom'
import DeskState from './DeskState/DeskState'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'

const CODE_MAX_LENGTH = 6
const CODE_REGEX_VALIDATION = /[^a-z0-9]/i

const CODE_ENTER = 'CODE_ENTER'
const CODE_TYPING = 'CODE_TYPING'

const CODE_SYNTAX_INVALID = 'CODE_SYNTAX_INVALID'
const CODE_ALREADY_USED = 'CODE_ALREADY_USED'
const CODE_VERIFICATION_IN_PROGRESS = 'CODE_VERIFICATION_IN_PROGRESS'
const CODE_VERIFICATION_SUCCESS = 'CODE_VERIFICATION_SUCCESS'
const CODE_VERIFICATION_FAILED = 'CODE_VERIFICATION_FAILED'
const CODE_REGISTERING_IN_PROGRESS = 'CODE_REGISTERING_IN_PROGRESS'
const CODE_REGISTERING_SUCCESS = 'CODE_REGISTERING_SUCCESS'
const CODE_REGISTERING_FAILED = 'CODE_REGISTERING_FAILED'

class Desk extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      booking: null,
      code: '',
      status: CODE_ENTER,
    }
    this.textInput = React.createRef()
  }

  componentDidMount() {
    this.textInput.current.focus()
  }

  handleOnClick = code => () => {
    this.handleCodeRegistration(code)
    this.textInput.current.focus()
  }

  handleSuccessWhenGetBookingFromCode = (state, action) => {
    const { payload } = action
    const booking = payload.datum

    const status = booking.isValidated ? CODE_ALREADY_USED : CODE_VERIFICATION_SUCCESS

    this.setState({ booking, status })
  }

  handleFailWhenGetBookingFromCode = (state, action) => {
    const {
      payload: { errors },
    } = action

    this.setState({
      status: CODE_VERIFICATION_FAILED,
      message: getRequestErrorStringFromErrors(errors),
    })
  }

  handleSuccessWhenValidateBooking = code => {
    const { trackValidateBookingSuccess } = this.props
    this.setState({ status: CODE_REGISTERING_SUCCESS })
    trackValidateBookingSuccess(code)
  }

  handleFailWhenValidateBooking = (state, action) => {
    const {
      payload: { errors },
    } = action

    this.setState({
      status: CODE_REGISTERING_FAILED,
      message: getRequestErrorStringFromErrors(errors),
    })
  }

  handleCodeChange = event => {
    const { getBookingFromCode } = this.props
    const code = event.target.value.toUpperCase()
    const status = this.getStatusFromCode(code)
    this.setState({ code, status })

    if (status === CODE_VERIFICATION_IN_PROGRESS) {
      getBookingFromCode(
        code,
        this.handleSuccessWhenGetBookingFromCode,
        this.handleFailWhenGetBookingFromCode
      )
    }
  }

  getStatusFromCode = code => {
    if (code === '') {
      return CODE_ENTER
    }

    if (code.match(CODE_REGEX_VALIDATION) !== null) {
      return CODE_SYNTAX_INVALID
    }

    if (code.length < CODE_MAX_LENGTH) {
      return CODE_TYPING
    }

    return CODE_VERIFICATION_IN_PROGRESS
  }

  handleCodeRegistration = code => {
    const { validateBooking } = this.props
    this.setState({ status: CODE_REGISTERING_IN_PROGRESS, code: '' })
    validateBooking(
      code,
      this.handleSuccessWhenValidateBooking(code),
      this.handleFailWhenValidateBooking
    )
  }

  getValuesFromStatus = status => {
    let { booking, code, message } = this.state
    let level

    switch (status) {
      case CODE_TYPING:
        message = `Caractères restants: ${CODE_MAX_LENGTH - code.length}/${CODE_MAX_LENGTH}`
        level = 'pending'
        break
      case CODE_SYNTAX_INVALID:
        message = 'Caractères valides : de A à Z et de 0 à 9'
        level = 'error'
        break
      case CODE_VERIFICATION_IN_PROGRESS:
        message = 'Vérification...'
        level = 'pending'
        break
      case CODE_ALREADY_USED:
        message = 'Ce coupon est déjà enregistré'
        level = 'error'
        break
      case CODE_VERIFICATION_SUCCESS:
        message = 'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
        level = 'pending'
        break
      case CODE_REGISTERING_IN_PROGRESS:
        message = 'Enregistrement en cours...'
        level = 'pending'
        break
      case CODE_REGISTERING_SUCCESS:
        message = 'Enregistrement réussi !'
        level = 'success'
        break
      case CODE_VERIFICATION_FAILED:
        level = 'error'
        break
      case CODE_REGISTERING_FAILED:
        level = 'error'
        break
      default:
        message = 'Saisissez un code'
        level = 'pending'
    }

    return {
      booking,
      level,
      message,
    }
  }

  renderChildComponent = () => {
    const { status } = this.state
    const { booking, level, message } = this.getValuesFromStatus(status)
    return (
      <DeskState
        booking={booking}
        level={level}
        message={message}
      />
    )
  }

  render() {
    const { code, status } = this.state

    return (
      <Main name="desk">
        <Titles title="Guichet" />
        <p className="advice">
          {'Enregistrez les codes de réservations présentés par les porteurs du pass.'}
        </p>
        <div className="section form">
          <p className="subtitle is-medium has-text-weight-bold">
            {'Scannez un code-barres ou saisissez-le ci-dessous :'}
          </p>

          <input
            className="input is-undefined"
            maxLength={CODE_MAX_LENGTH}
            name="code"
            onChange={this.handleCodeChange}
            ref={this.textInput}
            type="text"
            value={code}
          />

          <button
            className="primary-button"
            disabled={status !== CODE_VERIFICATION_SUCCESS}
            onClick={this.handleOnClick(code)}
            type="submit"
          >
            {'Valider'}
          </button>

          {this.renderChildComponent()}

          <Link
            className="primary-link"
            id="exitlink"
            to="/accueil"
          >
            {'Terminer'}
          </Link>
        </div>
      </Main>
    )
  }
}

Desk.propTypes = {
  getBookingFromCode: PropTypes.func.isRequired,
  trackValidateBookingSuccess: PropTypes.func.isRequired,
  validateBooking: PropTypes.func.isRequired,
}

export default Desk
