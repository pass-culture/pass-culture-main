import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../../layout/Icon/Icon'
import PropTypes from 'prop-types'
import { formatToFrenchDecimal } from '../../../utils/getDisplayPrice'
import { formatPublicName } from './domain/formatPublicName'
import { fetchLastHomepage } from '../../../vendor/contentful/contentful'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'
import Module from './Module/Module'
import BusinessModule from './BusinessModule/BusinessModule'
import ModuleWithCover from './ModuleWithCover/ModuleWithCover'

class Home extends Component {
  constructor(props) {
    super(props)
    this.state = {
      modules: []
    }
  }

  componentDidMount() {
    fetchLastHomepage().then(modules =>
      this.setState({
        modules: modules
      })
    )
  }

  renderModule = module => {
    if (module instanceof OffersWithCover) {
      return <ModuleWithCover module={module} />
    } else if (module instanceof Offers) {
      return <Module module={module} />
    }
    return <BusinessModule module={module} />
  }

  render() {
    const { modules } = this.state
    const { user } = this.props
    const { publicName, wallet_balance } = user
    const formattedPublicName = formatPublicName(publicName)
    const formattedWalletBalance = formatToFrenchDecimal(wallet_balance)
    const atLeastOneModule = modules.length > 0

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
          <h1>
            {`Bonjour ${formattedPublicName}`}
          </h1>
          <span>
            {`Tu as ${formattedWalletBalance} € sur ton pass`}
          </span>
        </div>
        {atLeastOneModule && (
          <div className="hw-modules">
            {modules.map(module => {
              return this.renderModule(module)
            })}
          </div>
        )}
      </div>
    )
  }
}

Home.propTypes = {
  user: PropTypes.shape({
    publicName: PropTypes.string,
    wallet_balance: PropTypes.number
  }).isRequired
}

export default Home
