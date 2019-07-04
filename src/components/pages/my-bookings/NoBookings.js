import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

const NoBookings = () => (
  <Fragment>
    <Link className="mb-link-offers" to="/decouverte">
      Lancez-vous
    </Link>
    <p className="mb-text">
      Dès que vous aurez réservé une offre,
      <br />
      vous la retrouverez ici.
    </p>
  </Fragment>
)

export default NoBookings
