import React from 'react'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import { Transition } from 'react-transition-group'

const duration = 500

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration}ms ease-in-out`,
}

const transitionStyles = {
  entered: { opacity: 1 },
  entering: { opacity: 0 },
  exited: { display: 'none', visibility: 'none' },
}

const DeckLoader = ({ isempty, isloading }) => {
  // on cache pas le loader
  // si il est en court de chargement
  // si il y a aucun produits à afficher pour l'utilisateur
  const shouldhide = !isloading && !isempty
  return (
    <Transition in={!shouldhide} timeout={duration}>
      {state => (
        <div
          id="deckloader"
          className="flex-rows flex-center is-overlay has-text-centered is-italic"
          style={{ ...defaultStyle, ...transitionStyles[state] }}
        >
          <Icon draggable={false} svg="ico-loading-card" alt="Chargement ..." />
          <h2 className="subtitle is-2">
            {isempty ? 'aucune offre pour le moment' : 'chargement des offres'}
          </h2>
        </div>
      )}
    </Transition>
  )
}

DeckLoader.defaultProps = {
  isempty: false,
}

DeckLoader.propTypes = {
  isempty: PropTypes.bool,
  isloading: PropTypes.bool.isRequired,
}

export default DeckLoader
