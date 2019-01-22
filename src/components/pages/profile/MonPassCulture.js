/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const MonPassCulture = ({ user }) => {
  const { expenses } = user
  const { actual: actualAll } = expenses.all
  const { actual: actualDigital } = expenses.digital
  const { actual: actualPhysical } = expenses.physical
  return (
    <div id="profile-page-user-wallet" className="jauges padded">
      <div className="text overall flex-1">
        <b className="is-block">{`Il reste ${actualAll} €`}</b>
        <span className="is-block fs14">sur votre Pass Culture</span>
      </div>
      <div className="text-containers flex-0 mt12 py12 mr8">
        <div className="fs14">
          <span className="is-block">
            jusqu&apos;à <b>{actualPhysical} €</b>
          </span>
          <span className="is-block">pour les biens culturels</span>
        </div>
        <div className="fs14 mt12">
          <span className="is-block">
            jusqu&apos;à <b>{actualDigital} €</b>
          </span>
          <span className="is-block">pour les offres numériques</span>
        </div>
      </div>
    </div>
  )
}

MonPassCulture.propTypes = {
  user: PropTypes.object.isRequired,
}

export default MonPassCulture
