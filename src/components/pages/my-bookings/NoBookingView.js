/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Link } from 'react-router-dom'

const NoBookingView = () => (
  <div className="is-full-layout flex-rows flex-center items-center">
    <p className="mb12">
      <Link
        to="/decouverte"
        className="is-white-text border-all border-white px24 py6"
      >
        <span className="fs22 is-medium">Lancez-vous</span>
      </Link>
    </p>
    <p className="is-white-text text-center">
      <span className="is-block">Dès que vous aurez réservé une offre,</span>
      <span className="is-block">vous la retrouverez ici.</span>
    </p>
  </div>
)

export default NoBookingView
