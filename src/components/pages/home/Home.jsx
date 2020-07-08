import React from 'react'
import { Link } from 'react-router-dom'
import Icon from '../../layout/Icon/Icon'
import PropTypes from 'prop-types'
import { formatToFrenchDecimal } from '../../../utils/getDisplayPrice'

const Home = ({ user }) => {
  const { publicName, wallet_balance } = user
  const formattedWalletBalance = formatToFrenchDecimal(wallet_balance)
  const variable = publicName.length < 15 ? 'title-small' : 'title-large'

  return (
    <div className="home-wrapper">
      <div className="hw-header">
        <div className="hw-account">
          <Link to="/profil">
            <Icon
              className="hw-account-image"
              svg="ico-informations-white"
            />
          </Link>
        </div>
        <h1 className={variable}>
          {`Bonjour ${publicName}`}
        </h1>
        <span>
          {`Tu as ${formattedWalletBalance}€ sur ton pass`}
        </span>
      </div>
    </div>
  )
}

Home.propTypes = {
  user: PropTypes.shape({
    publicName: PropTypes.string,
    wallet_balance: PropTypes.number,
  }).isRequired,
}

export default Home
