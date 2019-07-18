import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

const NoFavorites = () => (
  <Fragment>
    <Link
      className="mf-link-offers"
      to="/decouverte"
    >
      {'Lancez-vous'}
    </Link>
    <p className="mf-text">
      {'Dès que vous aurez ajouté une offre en favoris,'}
      <br />
      {'vous la retrouverez ici.'}
    </p>
  </Fragment>
)

export default NoFavorites
