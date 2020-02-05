import PropTypes from 'prop-types'
import React from 'react'

import formatDecimals from '../../../../utils/numbers/formatDecimals'

const Header = ({ currentUser }) => (
  <div
    className="flex-columns is-relative py16 fs18"
    id="main-menu-header"
  >
    <div className="column-profile text-center px18">
      <div id="main-menu-header-avatar">
        <img
          alt=""
          className="mb3"
          src="/icons/avatar-xl.svg"
        />
      </div>
      <div
        className="px5 is-hyphens"
        id="main-menu-header-username"
      >
        <span className="fs16 is-medium">
          {currentUser && currentUser.publicName}
        </span>
      </div>
    </div>
    <div className="column-account flex-1 flex-rows flex-center px18">
      <div className="fs30">
        <span>
          {'Mon pass'}
        </span>
      </div>
      <div id="main-menu-header-wallet-value">
        <span className="wallet-value">
          {currentUser && formatDecimals(currentUser.wallet_balance)}
        </span>
        <span className="currency">
          {'\u00A0€'}
        </span>
      </div>
    </div>
  </div>
)

Header.propTypes = {
  currentUser: PropTypes.shape().isRequired,
}

export default Header
