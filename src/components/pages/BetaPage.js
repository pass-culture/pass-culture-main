/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Link } from 'react-router-dom'

const BetaPage = () => (
  <div id="beta-page" className="pc-gradient page flex-rows">
    <main
      role="main"
      className="application-main flex-rows flex-around items-center"
    >
      <h1 className="has-text-centered">
        <i className="is-block">Bienvenue dans la version beta</i>
        <i className="is-block">du Pass Culture</i>
      </h1>
      <p className="has-text-centered">
        <i>
          Et merci de votre participation pour nous aider à l&apos;améliorer !
        </i>
      </p>
    </main>
    <footer
      role="navigation"
      className="application-footer dotted-top flex-columns items-center flex-end flex-0"
    >
      <Link to="/inscription" className="flex-center items-center">
        <i>C&apos;est par là</i>
        <span
          aria-hidden="true"
          className="icon-next"
          title="C&apos;est par là"
        />
      </Link>
    </footer>
  </div>
)

export default BetaPage
