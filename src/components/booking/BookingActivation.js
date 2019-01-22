/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

import { ActivationButton } from '../layout/buttons'

const renderIcon = () => (
  <span className="is-block mb12">
    <i
      className="icon-picto-info-solid"
      style={{ color: '#0166FC', fontSize: '5.4rem' }}
    />
  </span>
)

const renderHeader = () => (
  <span className="is-block mb36 fs16">
    <span className="is-block">Vous devez activer votre pass Culture pour</span>
    <span className="is-block">réserver une offre.</span>
  </span>
)

const BookingActivation = () => (
  <div id="booking-activation-block" className="flex-rows items-center">
    <h3 className="text-center">
      {renderIcon()}
      {renderHeader()}
    </h3>
    <p>
      <ActivationButton className="pc-theme-gradient px18 pt16 pb18 fs20">
        <span className="is-block">Activez votre pass Culture</span>
      </ActivationButton>
    </p>
  </div>
)

export default BookingActivation
