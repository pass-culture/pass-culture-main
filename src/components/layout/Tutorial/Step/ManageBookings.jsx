import React from 'react'

import Icon from '../../Icon'

import { ReactComponent as DownArrow } from './assets/down-arrow.svg'
import { ReactComponent as UpArrow } from './assets/up-arrow.svg'

const ManageBookings = () => (
  <>
    <h1>
      {'Suivre et gérer vos réservations'}
    </h1>
    <section className="mb-content">
      <span className="first-column">
        {'Valider vos contremarques'}
      </span>
      <span className="third-column">
        {'Accéder à la liste de vos réservations et les adresses mails'}
      </span>
      <DownArrow className="first-column" />
      <DownArrow className="third-column" />
      <span className="header-example">
        <span className="header-element">
          <Icon svg="ico-guichet-w" />
          {'Guichet'}
        </span>
        <span className="header-element">
          <Icon
            height="28"
            svg="ico-offres-w"
          />
          {'Offres'}
        </span>
        <span className="header-element">
          <Icon svg="ico-bookings-w" />
          {'Réservations'}
        </span>
        <span className="header-element">
          <Icon svg="ico-refunds" />
          {'Remboursements'}
        </span>
      </span>
      <UpArrow className="second-column" />
      <UpArrow className="fourth-column" />
      <span className="second-column">
        {'Créer, éditer, désactiver et gérer vos offres'}
      </span>
      <span className="fourth-column">
        {'Télécharger les remboursements du pass Culture'}
      </span>
    </section>
  </>
)

export default ManageBookings
