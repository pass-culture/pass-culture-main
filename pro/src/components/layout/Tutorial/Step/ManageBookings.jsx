import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as BookingsSvg } from 'components/layout/Header/assets/bookings.svg'
import { ReactComponent as CounterSvg } from 'components/layout/Header/assets/counter.svg'
import { ReactComponent as OffersSvg } from 'components/layout/Header/assets/offers.svg'
import { ReactComponent as RefundsSvg } from 'components/layout/Header/assets/refunds.svg'

import { ReactComponent as DownArrow } from './assets/down-arrow.svg'
import { ReactComponent as UpArrow } from './assets/up-arrow.svg'

const ManageBookings = ({ titleId }) => (
  <>
    <h1 id={titleId}>Suivre et gérer vos réservations</h1>
    <section className="mb-content">
      <span className="first-column">Validez vos contremarques</span>
      <span className="third-column">
        Accédez à la liste de vos réservations et les adresses mails des
        utilisateurs
      </span>
      <DownArrow className="first-column" />
      <DownArrow className="third-column" />
      <span className="header-example">
        <span className="header-element">
          <CounterSvg />
          Guichet
        </span>
        <span className="header-element">
          <OffersSvg />
          Offres
        </span>
        <span className="header-element">
          <BookingsSvg />
          Réservations
        </span>
        <span className="header-element">
          <RefundsSvg />
          Remboursements
        </span>
      </span>
      <UpArrow className="second-column" />
      <UpArrow className="fourth-column" />
      <span className="second-column">
        Créez, éditez, désactivez et gérez vos offres
      </span>
      <span className="fourth-column">
        Téléchargez les remboursements du pass Culture
      </span>
    </section>
  </>
)

ManageBookings.propTypes = {
  titleId: PropTypes.string.isRequired,
}

export default ManageBookings
