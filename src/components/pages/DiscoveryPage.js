import PropTypes from 'prop-types'
import {
  closeLoading,
  requestData,
  showLoading,
  Logger,
  withLogin,
} from 'pass-culture-shared'
import React from 'react'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { bindActionCreators, compose } from 'redux'
import { Route } from 'react-router-dom'

import Deck from '../Deck'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import DeckLoader from '../DeckLoader'
import BookingCard from '../BookingCard'
import { getQueryParams } from '../../helpers'
import { recommendationNormalizer } from '../../utils/normalizers'

const renderPageFooter = () => {
  const footerProps = { borderTop: true }
  return <Footer {...footerProps} />
}

class DiscoveryPage extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = props
    this.state = { haserror: false, isempty: false, isloading: true }
    const actions = { closeLoading, requestData, showLoading }
    this.actions = bindActionCreators(actions, dispatch)
  }

  componentDidMount() {
    Logger.log('DiscoveryPage ---> componentDidMount')
  }

  componentWillUnmount() {
    Logger.log('DiscoveryPage ---> componentWillUnmount')
  }

  handleRequestFail = () => {
    // ERREUR DE CHARGEMENT
    this.setState({ haserror: true, isloading: true })
  }

  handleRequestSuccess = (state, action) => {
    const { history, match } = this.props
    const { offerId, mediationId } = match.params
    const len = get(action, 'data.length')
    const isempty = !(len && len > 0)
    this.setState({ isempty, isloading: false })
    // NOTE -> on recharge pas la page
    // si l'URL contient déjà une offer et une mediation
    // car il s'agit alors d'une URL partagée
    const shouldNotReloadPage = isempty || (offerId && mediationId)
    if (shouldNotReloadPage) return
    const firstRecommendation = get(action, 'data[0]') || {}
    // NOTE -> si la premiere carte n'a pas d'offerid
    // alors il s'agit d'une carte tuto
    const firstOfferId =
      (firstRecommendation && firstRecommendation.offerId) || 'tuto'
    const firstMediationId =
      (firstRecommendation && firstRecommendation.mediationId) || ''
    history.push(`/decouverte/${firstOfferId}/${firstMediationId}`)
  }

  handleDataRequest = () => {
    const { match } = this.props
    this.setState({ isloading: true })
    // recupere les arguments depuis l'URL
    // l'API renvoi cette première carte avant les autres recommendations
    const query = getQueryParams(match)
    const serviceuri = `recommendations?${query}`
    this.actions.requestData('PUT', serviceuri, {
      handleFail: this.handleRequestFail,
      handleSuccess: this.handleRequestSuccess,
      normalizer: recommendationNormalizer,
    })
  }

  render() {
    const { backButton } = this.props
    const { isempty, isloading, haserror } = this.state
    return (
      <Main
        noPadding
        name="discovery"
        footer={renderPageFooter}
        handleDataRequest={this.handleDataRequest}
        backButton={backButton ? { className: 'discovery' } : null}
      >
        {!isloading && (
          // do not mount components if its loading
          <React.Fragment>
            <Route
              key="route-discovery-deck"
              path="/decouverte/:offerId/:mediationId?"
              render={route => <Deck {...route} />}
            />
            <Route
              key="route-discovery-booking"
              path="/decouverte/:offerId/:mediationId?/:view(booking|verso)"
              render={route => <BookingCard {...route} />}
            />
          </React.Fragment>
        )}
        <DeckLoader
          isempty={isempty}
          haserror={haserror}
          isloading={isloading}
        />
      </Main>
    )
  }
}

DiscoveryPage.defaultProps = {
  recommendations: null,
}

DiscoveryPage.propTypes = {
  backButton: PropTypes.bool.isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
}

const mapStateToProps = (state, ownProps) => ({
  backButton: ownProps.location.search.indexOf('to=verso') > -1,
})

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(DiscoveryPage)
