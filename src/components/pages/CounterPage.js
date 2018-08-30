import React, { Component } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { connect } from 'react-redux'
import { TextInput, Icon, SubmitButton } from 'pass-culture-shared'
import {
  wait,
  type,
  getVerification,
  postRegister,
  COUNTER_WAIT,
  COUNTER_TYPE,
} from '../../reducers/counter'
import Main from '../layout/Main'

class CounterPage extends Component {
  handleCodeChange(value) {
    if (value === '') {
      return this.props.wait()
    }

    if (value.length < 6) {
      return this.props.type(value)
    }
    // this.props.getVerification(value)
    // Hard code working case
    return this.props.getVerification('AE')
  }

  componentDidMount() {
    this.element.focus()
  }

  render() {
    const { counter } = this.props

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
          <button
            type="submit"
            onClick={() => getVerification(this.state.value)}>
            OK
          </button>

          {counter.state === COUNTER_WAIT && <div>Saissez un code</div>}
          {counter.state === COUNTER_TYPE && (
            <div>Le code doit contenir 6 caractères alphanumériques</div>
          )}

          {counter.state === 'COUNTER_GET_VERIFICATION' && (
            <div>Vérification...</div>
          )}

          {counter.state === 'COUNTER_RECEIVE_VERIFICATION' && (
            <div>
              Booking vérifié !
              <ul>
                <li>Identifiant : xxx</li>
                <li>Offre: {counter.booking.token}</li>
                <li>Date de l'offre: xxx</li>
              </ul>
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

const mapStateToProps = state => ({
  counter: state.counter,
})

const mapDispatchToProps = { wait, type, getVerification, postRegister }

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(CounterPage)
