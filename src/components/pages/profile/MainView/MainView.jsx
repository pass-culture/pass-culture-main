import PropTypes from 'prop-types'
import React from 'react'

import { version } from '../../../../../package.json'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import Header from '../Header/Header'
import RemainingCredit from '../RemainingCredit/RemainingCredit'
import User from '../ValueObjects/User'
import ListLinksContainer from '../ListLinks/ListLinksContainer'

const MainView = ({ user, historyPush }) => (
  <div className="mv-wrapper">
    <main className="mv-main">
      <div className="mv-scroll">
        <Header user={user} />
        <RemainingCredit user={user} />
        <ListLinksContainer historyPush={historyPush} />
        <section className="profile-section">
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
      </div>
    </main>
    <RelativeFooterContainer
      extraClassName="dotted-top-red"
      theme="white"
    />
  </div>
)

MainView.propTypes = {
  historyPush: PropTypes.func.isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default MainView
