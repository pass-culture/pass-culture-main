import React from 'react'
import { Link } from 'react-router-dom'

export const BetaPage = () => (
  <div className="beta-page page pc-gradient flex-rows">
    <main className="pc-main padded flex-rows flex-center">
      <h1>
        <div className="is-italic is-bold">{'Bienvenue'}</div>
        <div className="is-italic is-semi-bold">{'dans l’avant-première'}</div>
        <div className="is-italic is-normal">{'du pass Culture'}</div>
      </h1>
      <p className="is-italic is-medium mt36 fs22">
        {'Et merci de votre participation pour nous aider à l’améliorer !'}
      </p>
    </main>
    <footer className="pc-footer flex-columns flex-end">
      <Link
        className="flex-center items-center"
        id="beta-connexion-link"
        to="/connexion"
      >
        <span className="fs32 is-italic is-semi-bold">{'C’est par là'}</span>
        <span
          aria-hidden="true"
          className="pc-icon icon-legacy-next-long"
          title="C’est par là"
        />
      </Link>
    </footer>
  </div>
)

export default BetaPage
