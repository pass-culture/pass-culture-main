/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'

import { getAvailableBalanceByType } from './utils'
import { getWalletValue } from '../../../utils/user'

const MonPassCulture = ({ currentUser }) => {
  const { expenses } = currentUser || {}
  const allWallet = getWalletValue(currentUser)
  const { digital, physical } = expenses
  const [digitalAvailable, physicalAvailable] = [digital, physical].map(
    getAvailableBalanceByType(allWallet)
  )
  return (
    <div id="profile-page-user-wallet" className="jauges padded">
      <div className="text overall flex-1">
        <b className="is-block" id="profile-wallet-balance-value">
          {`Il reste ${allWallet} €`}
        </b>
        <span className="is-block fs14">sur votre Pass Culture</span>
      </div>
      <div className="text-containers flex-0 mt12 py12 mr8">
        <div className="fs14">
          <span className="is-block" id="profile-physical-wallet-value">
            Jusqu&apos;à <b>{physicalAvailable} €</b> pour les biens culturels
          </span>
        </div>
        <div className="fs14 mt12">
          <span className="is-block" id="profile-digital-wallet-value">
            Jusqu&apos;à <b>{digitalAvailable} €</b> pour les offres numériques
          </span>
        </div>
      </div>
    </div>
  )
}

MonPassCulture.propTypes = {
  currentUser: PropTypes.object.isRequired,
}

export default MonPassCulture
