import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Transition } from 'react-transition-group'

import AbsoluteFooterContainer from '../AbsoluteFooter/AbsoluteFooterContainer'
import Icon from '../Icon/Icon'
import LoadingAnimation from '../LoadingPage/LoadingAnimation/LoadingAnimation'

const duration = 500

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration * 3}ms ease-in-out`, // longer duration is used to hide deck animation as cards are added to it
}

const transitionStyles = {
  entered: { opacity: 1, transition: `opacity ${duration}ms ease-in-out` },
  entering: { opacity: 1, transition: `opacity ${duration}ms ease-in-out` },

  exited: { display: 'none', visibility: 'none' },
}

class Loader extends PureComponent {
  constructor(props) {
    super(props)

    this.state = { isFirstLoad: true }
  }

  componentDidUpdate(prevProps) {
    this.handleFirstLoad(prevProps)
  }

  handleFirstLoad = prevProps => {
    const { isLoading } = this.props

    if (prevProps.isLoading && !isLoading) {
      this.setState({ isFirstLoad: false })
    }
  }

  handleRefresh = () => window.location.reload()

  renderIcon = () => {
    const { isLoading, statusCode } = this.props

    if (isLoading) {
      return <LoadingAnimation />
    }

    if (statusCode === 500) {
      return <Icon svg="logo-error" />
    }
  }

  renderTitle = () => {
    const { statusCode } = this.props

    if (statusCode === 500) {
      return 'Oops !'
    }
  }

  renderMessage = () => {
    const {
      hasError,
      isEmpty,
      isLoading,
      match: { params },
      statusCode,
    } = this.props
    const atDecksEnd = params.mediationId === 'fin'
    const { isFirstLoad } = this.state

    if (hasError) {
      if (statusCode === 500) {
        return 'Une erreur s’est produite pendant le chargement des offres.'
      }
      return 'Erreur de chargement'
    }
    if (isLoading && (atDecksEnd || isFirstLoad)) {
      return 'Chargement en cours…'
    }
    if (isEmpty && !atDecksEnd) {
      return 'Aucune offre pour le moment ! Revenez bientôt pour découvrir les nouveautés.'
    }
    return ''
  }

  renderRefreshButton = () => {
    const { statusCode } = this.props

    if (statusCode === 500) {
      return (
        <button
          className="loader-refresh"
          onClick={this.handleRefresh}
          type="button"
        >
          {'Réessayer'}
        </button>
      )
    }
  }

  render() {
    const {
      hasError,
      isEmpty,
      isLoading,
      match: { params },
    } = this.props
    const atDecksEnd = params.mediationId === 'fin'
    const { isFirstLoad } = this.state
    // on cache pas le loader
    // si il est en court de chargement et qu'on est à la fin du Deck
    // si il y a aucun produits à afficher pour l'utilisateur
    const showFooter = isEmpty || hasError
    const shouldHide = !(isLoading && (atDecksEnd || isFirstLoad)) && !isEmpty && !hasError

    return (
      <Transition
        in={!shouldHide}
        out={shouldHide}
        timeout={duration}
      >
        {status => (
          <div
            className="loader"
            style={{ ...defaultStyle, ...transitionStyles[status] }}
          >
            {this.renderIcon()}

            <p className="loader-title">
              {this.renderTitle()}
            </p>

            <p className="loader-message">
              {this.renderMessage()}
            </p>

            {this.renderRefreshButton()}

            {showFooter && (
              <AbsoluteFooterContainer
                areDetailsVisible={false}
                borderTop
                colored={false}
              />
            )}
          </div>
        )}
      </Transition>
    )
  }
}

Loader.defaultProps = {
  hasError: false,
  isEmpty: false,
  statusCode: 200,
}

Loader.propTypes = {
  hasError: PropTypes.bool,
  isEmpty: PropTypes.bool,
  isLoading: PropTypes.bool.isRequired,
  match: PropTypes.shape().isRequired,
  statusCode: PropTypes.number,
}

export default Loader
