import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'pass-culture-shared'

import Main from '../layout/Main'

const COUNTER_WAIT = 'COUNTER_WAIT'
const COUNTER_TYPE = 'COUNTER_TYPE'
const COUNTER_INVALID = 'COUNTER_INVALID'
const COUNTER_GET_VERIFICATION = 'COUNTER_GET_VERIFICATION'
const COUNTER_RECEIVE_VERIFICATION = 'COUNTER_RECEIVE_VERIFICATION'
const COUNTER_FAIL_VERIFICATION = 'COUNTER_FAIL_VERIFICATION'
const COUNTER_POST_REGISTER = 'COUNTER_POST_REGISTER'
const COUNTER_RECEIVE_REGISTER = 'COUNTER_RECEIVE_REGISTER'
const COUNTER_FAIL_REGISTER = 'COUNTER_FAIL_REGISTER'

class CounterPage extends Component {
  constructor(props) {
    super(props)

    const { dispatch } = props

    this.actions = bindActionCreators({ requestData }, dispatch)

    this.state = {
      state: COUNTER_WAIT,
      code: '',
      booking: null,
    }
  }

  receiveVerification(status, booking) {
    this.setState({
      state: COUNTER_RECEIVE_VERIFICATION,
      booking,
    })
  }

  getVerification(code) {
    this.actions.requestData('GET', `/bookings/AE`, {
      key: 'bookings',
      handleSuccess: (state, request) => {
        this.receiveVerification(200, request.data)
      },
      handleFail: (state, request) => {
        this.setState({ state: COUNTER_FAIL_VERIFICATION })
        console.log(request.errors)
      },
    })
  }

  handleCodeChange(event) {
    const value = event.target.value

    this.setState({ code: value })

    if (value === '') {
      return this.setState({ state: COUNTER_WAIT })
    }

    if (value.match(/[^a-z0-9]/i) !== null) {
      return this.setState({ state: COUNTER_INVALID })
    }

    if (value.length < 6) {
      return this.setState({ state: COUNTER_TYPE })
    }

    this.setState({ state: COUNTER_GET_VERIFICATION })
    return this.getVerification(value)
  }

  handleCodeRegistration(code) {
    this.setState({ state: COUNTER_POST_REGISTER })
    this.actions.requestData('POST', '/some/url', {
      body: {
        code,
      },
      handleSuccess: (state, request) => {
        this.setState({ state: COUNTER_RECEIVE_REGISTER })
      },
      handleFail: (state, request) => {
        this.setState({ state: COUNTER_FAIL_REGISTER })
      },
    })
  }

  componentDidMount() {
    this.element.focus()
  }

  bookingDetail = booking => (
    <div>
      <ul>
        <li>Identifiant : xxx</li>
        <li>Offre: {booking.token}</li>
        <li>Date de l'offre: xxx</li>
      </ul>
    </div>
  )

  render() {
    return (
      <Main name="counter">
        <div className="section hero">
          <h1 className="main-title">Guichet</h1>
          <p className="subtitle">
            Enregistrez les codes de réservations présentés par les porteurs du
            Pass.
          </p>
        </div>

        <div className="section">
          <p className="subtitle is-medium has-text-weight-bold">
            Scannez un code-barres, ou saisissez-le ci-dessous:
          </p>
          <input
            className="input is-undefined"
            type="text"
            ref={el => (this.element = el)}
            name="code"
            onChange={this.handleCodeChange.bind(this)}
          />

          {this.state.state === COUNTER_RECEIVE_VERIFICATION && (
            <button
              type="submit"
              onClick={() => this.handleCodeRegistration(this.state.code)}>
              OK
            </button>
          )}

          {this.state.state === COUNTER_WAIT && <div>Saissez un code</div>}
          {this.state.state === COUNTER_TYPE && (
            <div>
              caractères restants: {6 - this.state.code.length}
              /6
            </div>
          )}

          {this.state.state === COUNTER_INVALID && (
            <div>
              Le code ne doit contenir que des caractères alphanumériques (de A
              à Z et de 0 à 9)
            </div>
          )}

          {this.state.state === COUNTER_GET_VERIFICATION && (
            <div>Vérification...</div>
          )}

          {this.state.state === COUNTER_RECEIVE_VERIFICATION && (
            <div>
              <span>Booking vérifié !</span>
              {this.bookingDetail(this.state.booking)}
            </div>
          )}

          {this.state.state === COUNTER_POST_REGISTER && (
            <div>
              <span>Enregistrement en cours...</span>
              {this.bookingDetail(this.state.booking)}
            </div>
          )}

          {this.state.state === COUNTER_RECEIVE_REGISTER && (
            <div>
              <span>Enregistrement réussi!</span>
              {this.bookingDetail(this.state.booking)}
            </div>
          )}

          {this.state.state === COUNTER_FAIL_REGISTER && (
            <div>
              <span>Echec de l'enregistrement (problème technique)</span>
              {this.bookingDetail(this.state.booking)}
            </div>
          )}
        </div>

        <NavLink
          className="button is-primary is-medium is-pulled-right"
          to="/offres">
          Terminer
        </NavLink>
      </Main>
    )
  }
}

export default connect()(CounterPage)
