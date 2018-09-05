/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Link } from 'react-router-dom'

const BetaPage = () => (
  <div id="beta-page" className="pc-gradient page flex-rows">
    <main role="main" className="pc-main padded flex-rows flex-center flex-0">
      <h1 className="text-left fs32">
        <b>
          <i className="is-block">Bienvenue</i>
        </b>
        <i className="is-block">dans la version beta</i>
        <i className="is-block">du Pass Culture</i>
      </h1>
      <p className="text-left mt36 fs22">
        <i className="is-block">Et merci de votre participation</i>
        <i className="is-block">pour nous aider à l&apos;améliorer !</i>
      </p>
    </main>
    <footer
      role="navigation"
      className="pc-footer flex-columns items-center flex-end flex-0"
      style={{ borderTop: '4px dotted #FFFFFF' }}
    >
      <Link to="/inscription" className="flex-center items-center">
        <b className="fs32">
          <i>C&apos;est par là</i>
        </b>
        <span
          aria-hidden="true"
          className="icon-next-long"
          title="C&apos;est par là"
        />
      </Link>
    </footer>
  </div>
)

export default BetaPage
