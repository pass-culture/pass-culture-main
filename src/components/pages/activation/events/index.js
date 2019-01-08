/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withLogin } from 'pass-culture-shared'

import ActivationFormWrapper from './form'
import ActivationFormFooter from './footer'
import ActivationFormHeader from './header'
import { mapDispatchToProps, mapStateToProps } from './connect'

class ActivationEvents extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { hasError: false, isLoading: true }
  }

  componentDidMount() {
    const { getAllActivationOffers } = this.props
    getAllActivationOffers(this.handleRequestFail, this.handleRequestSuccess)
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
      <div
        id="activation-page"
        className="page is-relative pc-gradient is-white-text flex-rows"
      >
        <main
          role="main"
          className="pc-main p24 is-clipped is-relative flex-1 flex-rows flex-center align-center"
        >
          <ActivationFormHeader />
          {!hasError && (
            <ActivationFormWrapper
              isLoading={isLoading}
              offers={offers}
              onFormSubmit={this.onFormSubmit}
            />
          )}
          {(hasError && this.renderErrorText()) || null}
        </main>
        <ActivationFormFooter />
      </div>
    )
  }
}

ActivationEvents.propTypes = {
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
