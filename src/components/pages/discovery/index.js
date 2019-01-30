import PropTypes from 'prop-types'
import { assignData, requestData, withLogin } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Route } from 'react-router-dom'

import Deck from './Deck'
import Booking from '../../booking'
import BackButton from '../../layout/BackButton'
import Loader from '../../layout/Loader'
import Footer from '../../layout/Footer'
import { getQueryParams } from '../../../helpers'
import { recommendationNormalizer } from '../../../utils/normalizers'

export class RawDiscoveryPage extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      haserror: false,
      isempty: false,
      isloading: true,
    }
  }

  componentDidMount() {
    this.handleDataRequest()
  }

  componentWillUnmount() {
    const { dispatch } = this.props
    dispatch(assignData({ recommendations: [], seenRecommendations: [] }))
  }

  handleRequestFail = () => {
    this.setState({ haserror: true, isloading: true }, () => {
      const { history } = this.props
      const delayBeforeRedirect = 2000
      setTimeout(() => history.replace('/connexion'), delayBeforeRedirect)
    })
  }

  handleRequestSuccess = (state, action) => {
    const { dispatch, history, match } = this.props
    const { offerId, mediationId } = match.params
    const len = get(action, 'data.length')
    const isempty = !(len && len > 0)
    // loading
    this.setState({ isempty, isloading: false })
    // clear the cache of seen cards
    dispatch(assignData({ readRecommendations: [] }))
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
    // replace pluto qu'un push permet de recharger les données
    // quand on fait back dans le navigateur et qu'on revient
    // à l'URL /decouverte
    history.replace(`/decouverte/${firstOfferId}/${firstMediationId}`)
  }

  handleDataRequest = () => {
    const {
      dispatch,
      match,
      readRecommendations,
      seenRecommendations,
    } = this.props

    this.setState({ isloading: true })
    // recupere les arguments depuis l'URL
    // l'API renvoi cette première carte avant les autres recommendations
    const queryString = getQueryParams(match, readRecommendations)
    const serviceuri = `recommendations?${queryString}`

    dispatch(
      requestData('PUT', serviceuri, {
        body: {
          readRecommendations,
          seenRecommendationIds:
            seenRecommendations && seenRecommendations.map(r => r.id),
        },
        handleFail: this.handleRequestFail,
        handleSuccess: this.handleRequestSuccess,
        normalizer: recommendationNormalizer,
      })
    )
  }

  render() {
    const { match } = this.props
    const { haserror, isempty, isloading } = this.state

    const withBackButton = match.params.view === 'verso'

    return (
      <Fragment>
        <main
          role="main"
          className="discovery-page no-padding page with-footer"
        >
          {withBackButton && <BackButton />}
          {!isloading && (
            // do not mount components if its loading
            <Fragment>
              <Route
                key="route-discovery-booking"
                path="/decouverte/:offerId/:mediationId?/:view(booking)"
                render={route => <Booking {...route} />}
              />
              <Route
                key="route-discovery-deck"
                path="decouverte/:offerId/:mediationId?/:view(verso|cancelled)?/:bookingId?"
                render={route => (
                  <Deck {...route} handleDataRequest={this.handleDataRequest} />
                )}
              />
            </Fragment>
          )}
          <Footer borderTop />
        </main>
        <Loader isempty={isempty} haserror={haserror} isloading={isloading} />
      </Fragment>
    )
  }
}

RawDiscoveryPage.defaultProps = {
  readRecommendations: null,
  seenRecommendations: null,
}

RawDiscoveryPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  readRecommendations: PropTypes.array,
  seenRecommendations: PropTypes.array,
}

const mapStateToProps = state => ({
  readRecommendations: state.data.readRecommendations,
  seenRecommendations: state.data.seenRecommendations,
})

const DiscoveryPage = compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(RawDiscoveryPage)

export default DiscoveryPage
