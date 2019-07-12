import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import BookingContainer from '../../booking/BookingContainer'
import { recommendationNormalizer } from '../../../utils/normalizers'
import RectoContainer from '../../recto/RectoContainer'
import VersoContainer from '../../verso/VersoContainer'

class SearchDetails extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { forceDetailsVisible: false }
  }

  componentDidMount() {
    const { recommendation } = this.props

    if (recommendation) {
      // We need to wait to go out the mount lifecycle
      // in order to force the dom to render
      // twice
      setTimeout(this.handleForceDetailsVisible)
      return
    }

    this.handleRequestData()
  }

  handleRequestData = () => {
    const { dispatch, match } = this.props
    const {
      params: { mediationIdOrView, offerId },
    } = match
    const mediationId = mediationIdOrView === 'booking' ? null : mediationIdOrView
    let apiPath = `/recommendations/offers/${offerId}`

    if (mediationId) {
      apiPath = `${apiPath}?mediationId=${mediationId}`
    }

    dispatch(
      requestData({
        apiPath,
        handleSuccess: this.handleForceDetailsVisible,
        normalizer: recommendationNormalizer,
        stateKeys: 'searchRecommendations',
      })
    )
  }

  handleForceDetailsVisible = () => {
    this.setState({ forceDetailsVisible: true })
  }

  renderSearchResultRoute = route => (<BookingContainer
    extraClassName="with-header"
    {...route}
                                      />)

  render() {
    const { recommendation } = this.props
    const { forceDetailsVisible } = this.state

    return (
      <Fragment>
        {forceDetailsVisible && (
          <Route
            path="/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/(booking|cancelled)/:bookingId?"
            render={this.renderSearchResultRoute}
          />
        )}
        {recommendation && (
          <Fragment>
            <VersoContainer
              extraClassName="with-header"
              forceDetailsVisible={forceDetailsVisible}
              recommendation={recommendation}
            />
            <RectoContainer
              areDetailsVisible={forceDetailsVisible}
              extraClassName="with-header"
              position="current"
              recommendation={recommendation}
            />
          </Fragment>
        )}
      </Fragment>
    )
  }
}

SearchDetails.defaultProps = {
  recommendation: null,
}

SearchDetails.propTypes = {
  dispatch: PropTypes.func.isRequired,
  match: PropTypes.shape().isRequired,
  recommendation: PropTypes.shape(),
}

export default SearchDetails
