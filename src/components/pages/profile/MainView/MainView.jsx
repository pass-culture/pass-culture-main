import PropTypes from 'prop-types'
import React from 'react'

import { version } from '../../../../../package.json'
import Header from '../Header/Header'
import RemainingCredit from '../RemainingCredit/RemainingCredit'
import User from '../ValueObjects/User'
import ListLinksContainer from '../ListLinks/ListLinksContainer'

const MainView = ({ user, historyPush }) => (
  <main className="pf-container">
    <Header user={user} />
    <RemainingCredit user={user} />
    <ListLinksContainer historyPush={historyPush} />
    <section className="pf-section">
      <div className="mv-app-version">
        {`Version ${version}`}
      </div>
      <img
        alt=""
        className="mv-ministry-of-culture"
        src="/min-culture-rvb@2x.png"
        width="161"
      />
    </section>
  </main>
)

MainView.propTypes = {
  historyPush: PropTypes.func.isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default MainView
