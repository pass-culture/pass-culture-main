/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../utils/config'
import { isUserActivated } from '../../utils/user'
import { ActivationButton } from '../layout/buttons'

const MenuHeader = ({ toggleMainMenu, user }) => {
  const wallet = user ? user.wallet_balance : '——'
  const isActivated = isUserActivated(user)
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
          {/* Solde restant sur le compte user */}
          {isActivated && (
            <span className="fs52 is-normal" style={{ lineHeight: '42px' }}>
              {`${wallet}€`}
            </span>
          )}
          {/* Bouton d'activation du compte user */}
          {!isActivated && (
            <ActivationButton
              className="fs18 py12 is-full-width pc-theme-dark-primary"
              onClickHandler={toggleMainMenu}
            />
          )}
        </p>
      </div>
    </div>
  )
}

MenuHeader.defaultProps = {
  user: null,
}

MenuHeader.propTypes = {
  toggleMainMenu: PropTypes.func.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

export default MenuHeader
