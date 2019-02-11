/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const MonPassCulture = ({ user }) => {
  const { expenses } = user
  const allWallet = expenses.all.max - expenses.all.actual
  const digitalWallet = expenses.digital.max - expenses.digital.actual
  const physicalWallet = expenses.physical.max - expenses.physical.actual
  return (
    <div id="profile-page-user-wallet" className="jauges padded">
      <div className="text overall flex-1">
        <b className="is-block">{`Il reste ${allWallet} €`}</b>
        <span className="is-block fs14">sur votre Pass Culture</span>
      </div>
      <div className="text-containers flex-0 mt12 py12 mr8">
        <div className="fs14">
          <span className="is-block">
            Jusqu&apos;à <b>{physicalWallet} €</b> pour les biens culturels
          </span>
        </div>
        <div className="fs14 mt12">
          <span className="is-block">
            Jusqu&apos;à <b>{digitalWallet} €</b> pour les offres numériques
          </span>
        </div>
      </div>
    </div>
  )
}

MonPassCulture.propTypes = {
  user: PropTypes.object.isRequired,
}

export default MonPassCulture
