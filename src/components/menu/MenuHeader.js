/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'

import { selectCurrentUser } from '../hocs'
import { ROOT_PATH } from '../../utils/config'
import { getWalletValue } from '../../utils/user'

export const RawMenuHeader = ({ currentUser }) => {
  const walletValue = getWalletValue(currentUser)
  const avatar = `${ROOT_PATH}/icons/avatar-default-w-XL.svg`
  return (
    <div id="main-menu-header" className="flex-columns is-relative py16 fs18">
      <div className="column-profile text-center px18">
        <p id="main-menu-header-avatar">
          <img alt="" src={avatar} className="mb3" />
        </p>
        <p id="main-menu-header-username" className="px5 is-hyphens">
          <span className="fs16 is-medium">
            {currentUser && currentUser.publicName}
          </span>
        </p>
      </div>
      <div className="column-account flex-1 flex-rows flex-center px18">
        <p className="fs30">
          <span>Mon Pass</span>
        </p>
        <p id="main-menu-header-wallet-value">
          <span
            className="fs44 is-semi-bold"
            style={{ letterSpacing: '-0.1rem', lineHeight: '42px' }}
          >
            {walletValue}
          </span>
          <span className="fs30" style={{ lineHeight: '42px' }}>
            &nbsp;€
          </span>
        </p>
      </div>
    </div>
  )
}

RawMenuHeader.defaultProps = {
  currentUser: null,
}

RawMenuHeader.propTypes = {
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(RawMenuHeader)
