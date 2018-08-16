/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Transition } from 'react-transition-group'

const duration = 500

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration}ms ease`,
}

const transitionStyles = {
  entered: { opacity: 1 },
  entering: { opacity: 0 },
  exited: { display: 'none', visibility: 'none' },
}

const BookingUserUndefined = ({ show }) => (
  <Transition in={show} timeout={(!show && duration) || 0}>
    {state => (
      <div className="" style={{ ...defaultStyle, ...transitionStyles[state] }}>
        {/* <Icon  */}
        <p>
          Cette offre est nominaitve: merci de remplir votre Nom et Prénom dans
          la rubrique <b>Profil</b>
          {''}
          pour en profiter.
        </p>
      </div>
    )}
  </Transition>
)

BookingUserUndefined.propTypes = {
  show: PropTypes.bool.isRequired,
}

export default BookingUserUndefined
