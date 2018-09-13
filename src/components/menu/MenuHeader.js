/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../utils/config'

const MenuHeader = ({ user }) => {
  const wallet = '--'
  const avatar = `${ROOT_PATH}/icons/avatar-default-w-XL.svg`
  return (
    <div id="main-menu-header" className="flex-columns is-relative py16 fs18">
      <div className="profile text-center">
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
      <div className="account flex-center flex-rows text-center">
        <p className="fs30">
          <span>Mon Pass</span>
        </p>
        <p id="main-menu-header-wallet-value" className="fs48">
          <span>{`${wallet}€`}</span>
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
