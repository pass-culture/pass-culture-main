/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Link } from 'react-router-dom'

import { withNotRequiredLogin } from '../hocs'

export const RawBetaPage = () => (
  <div
    className="page pc-gradient flex-rows"
    id="beta-page"
  >
    <main
      className="pc-main padded flex-rows flex-center flex-0"
      role="main"
    >
      <h1 className="text-left fs32">
        <span className="is-bold is-italic is-block">Bienvenue</span>
        <span className="is-italic is-block is-semi-bold">
          dans l&apos;avant-première
        </span>
        <span className="is-italic is-block">du Pass Culture</span>
      </h1>
      <p className="text-left is-italic is-medium mt36 fs22">
        <span className="is-block">
          Et merci de votre participation pour nous aider à
          l&apos;améliorer&nbsp;!
        </span>
      </p>
    </main>
    <footer
      className="pc-footer flex-columns flex-end"
      role="navigation"
    >
      <Link
        className="flex-center items-center"
        id="beta-connexion-link"
        to="/connexion"
      >
        <span className="fs32 is-italic is-semi-bold">C&apos;est par là</span>
        <span
          aria-hidden="true"
          className="pc-icon icon-legacy-next-long"
          title="C'est par là"
        />
      </Link>
    </footer>
  </div>
)

export default withNotRequiredLogin(RawBetaPage)
