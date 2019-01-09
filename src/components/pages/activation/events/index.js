/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { toast } from 'react-toastify'
import { withLogin } from 'pass-culture-shared'

import ActivationEventsForm from './form'
import ActivationEventsFooter from './footer'
import ActivationEventsHeader from './header'
import ActivationEventsEmail from './email-button'
import { mapDispatchToProps, mapStateToProps } from './connect'

class ActivationEvents extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { hasError: false, isLoading: true }
  }

  componentDidMount() {
    const { getAllActivationOffers, fromPassword } = this.props
    getAllActivationOffers(this.handleRequestFail, this.handleRequestSuccess)
    if (!fromPassword) return
    const delay = 1000
    const autoClose = 3000
    const message = 'Votre mot de passe a bien été enregistré.'
    setTimeout(() => toast(message, { autoClose }), delay)
  }

  handleRequestFail = () => {
    const nextstate = { hasError: true, isLoading: false }
    this.setState(nextstate)
  }

  handleRequestSuccess = () => {
    const nextstate = { hasError: false, isLoading: false }
    this.setState(nextstate)
  }

  renderErrorText = () => (
    <p>Une erreur s&apos;est produite veuillez recharger la page</p>
  )

  render() {
    const { offers } = this.props
    const { hasError, isLoading } = this.state
    return (
      <div id="activation-events-page" className="is-full-layout flex-rows">
        <main role="main" className="pc-main padded-2x flex-rows flex-center">
          <ActivationEventsHeader />
          <ActivationEventsEmail />
          {!hasError && (
            <ActivationEventsForm isLoading={isLoading} offers={offers} />
          )}
          {(hasError && this.renderErrorText()) || null}
        </main>
        <ActivationEventsFooter />
      </div>
    )
  }
}

ActivationEvents.propTypes = {
  fromPassword: PropTypes.bool.isRequired,
  getAllActivationOffers: PropTypes.func.isRequired,
  offers: PropTypes.array.isRequired,
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(ActivationEvents)
