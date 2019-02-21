/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../utils/config'
import { getWalletValue } from '../../utils/user'

const MenuHeader = ({ user }) => {
  const walletValue = getWalletValue(user)
  const avatar = `${ROOT_PATH}/icons/avatar-default-w-XL.svg`
  return (
    <div id="main-menu-header" className="flex-columns is-relative py16 fs18">
      <div className="column-profile text-center">
        <p id="main-menu-header-avatar">
          <img alt="" src={avatar} className="mb3" />
        </p>
        <p
          id="main-menu-header-username"
          className="is-clipped text-ellipsis px5"
        >
          <span>{user && user.publicName}</span>
        </p>
      </div>
      <div className="column-account flex-1 flex-rows flex-center px12">
        <p className="fs30 mb12">
          <span>Mon Pass</span>
        </p>
        <p id="main-menu-header-wallet-value">
          <span className="fs52 is-normal" style={{ lineHeight: '42px' }}>
            {walletValue}&nbsp;€
          </span>
        </p>
      </div>
    </div>
  )
}

MenuHeader.defaultProps = {
  user: null,
}

MenuHeader.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

export default MenuHeader
