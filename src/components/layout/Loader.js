import React from 'react'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import { Transition } from 'react-transition-group'

import NavigationFooter from './NavigationFooter'

const duration = 500

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration}ms ease-in-out`,
}

const transitionStyles = {
  entered: { opacity: 1 },
  entering: { opacity: 1 },
  exited: { display: 'none', visibility: 'none' },
}

const Loader = ({ haserror, isempty, isloading }) => {
  // on cache pas le loader
  // si il est en court de chargement
  // si il y a aucun produits à afficher pour l'utilisateur
  const showfooter = isempty || haserror
  const shouldhide = !isloading && !isempty && !haserror
  return (
    <Transition in={!shouldhide} timeout={duration}>
      {state => (
        <div
          id="application-loader"
          style={{ ...defaultStyle, ...transitionStyles[state] }}
        >
          <Icon
            draggable={false}
            svg="ico-loading-card"
            alt="Chargement en cours. Merci de patienter…"
          />
          <h2 className="fs20">
            {(isempty && 'Aucune offre pour le moment') || ''}
            {/* // FIXME -> mettre un label plus sexy avec redirection */}
            {(haserror && 'Erreur de chargement') || ''}
            {(!isempty && !haserror && 'Chargement des offres') || ''}
          </h2>
          {showfooter && <NavigationFooter />}
        </div>
      )}
    </Transition>
  )
}

Loader.defaultProps = {
  haserror: false,
  isempty: false,
}

Loader.propTypes = {
  haserror: PropTypes.bool,
  isempty: PropTypes.bool,
  isloading: PropTypes.bool.isRequired,
}

export default Loader
