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
    let component
    if (module instanceof OffersWithCover) {
      component = <ModuleWithCover module={module} />
    } else if (module instanceof Offers) {
      component = <Module module={module} />
    } else {
      component = <BusinessModule module={module} />
    }
    return component
  }

  render() {
    const { modules } = this.state
    const { user } = this.props
    const { publicName, wallet_balance } = user
    const formattedPublicName = formatPublicName(publicName)
    const formattedWalletBalance = formatToFrenchDecimal(wallet_balance)

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
            {`Tu as ${formattedWalletBalance}€ sur ton pass`}
          </span>
        </div>
        <div className="hw-modules">
          {modules.length > 0 && modules.map(module => {
            return this.renderModule(module)
          })}
        </div>
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
