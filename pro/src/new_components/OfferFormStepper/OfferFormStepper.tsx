import React from 'react'
import { Link } from 'react-router-dom'

const OfferFormStepper = (): JSX.Element => {
  return (
    <ul>
      <li>
        <Link to="/offre/individuelle/informations">Informations</Link>
      </li>
      <li>
        <Link to="/offre/individuelle/lieu">Lieu</Link>
      </li>
    </ul>
  )
}

export default OfferFormStepper
