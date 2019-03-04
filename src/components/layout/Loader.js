import React from 'react'
import { withRouter } from 'react-router-dom'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import { Transition } from 'react-transition-group'

import NavigationFooter from './NavigationFooter'

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

export class RawLoader extends React.PureComponent {
  constructor() {
    super()
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

  renderMessage = () => {
    const {
      hasError,
      isEmpty,
      isLoading,
      match: { params },
    } = this.props
    const atDecksEnd = params.mediationId === 'fin'
    const { isFirstLoad } = this.state

    if (hasError) {
      return 'Erreur de chargement'
    }
    if (isLoading && (atDecksEnd || isFirstLoad)) {
      return 'Chargement des offres'
    }
    if (isEmpty && !atDecksEnd) {
      return 'Aucune offre pour le moment ! Revenez bientôt pour découvrir les nouveautés.'
    }
    return ''
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
    const shouldHide =
      !(isLoading && (atDecksEnd || isFirstLoad)) && !isEmpty && !hasError
    return (
      <Transition in={!shouldHide} out={shouldHide} timeout={duration}>
        {status => (
          <div
            id="application-loader"
            className="flex-rows"
            style={{ ...defaultStyle, ...transitionStyles[status] }}
          >
            <div className="flex-1 flex-rows flex-center">
              {isLoading && (
                <Icon draggable={false} svg="ico-loading-card" alt="" />
              )}
              <h2 className="fs20">
                {this.renderMessage()}
              </h2>
            </div>
            {showFooter && (
              <NavigationFooter
                theme="transparent"
                className="dotted-top-white"
              />
            )}
          </div>
        )}
      </Transition>
    )
  }
}

RawLoader.defaultProps = {
  hasError: false,
  isEmpty: false,
}

RawLoader.propTypes = {
  hasError: PropTypes.bool,
  isEmpty: PropTypes.bool,
  isLoading: PropTypes.bool.isRequired,
  match: PropTypes.object.isRequired,
}

export const Loader = withRouter(RawLoader)
