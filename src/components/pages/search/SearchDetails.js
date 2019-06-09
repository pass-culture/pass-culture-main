import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'
import { Route } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import BookingContainer from '../../booking/BookingContainer'
import { recommendationNormalizer } from '../../../utils/normalizers'
import RectoContainer from '../../recto/RectoContainer'
import VersoContainer from '../../verso/VersoContainer'

export class SearchDetails extends PureComponent {
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
    const mediationId =
      mediationIdOrView === 'booking' ? null : mediationIdOrView
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

  render() {
    const { recommendation } = this.props
    const { forceDetailsVisible } = this.state

    return (
      <Fragment>
        {forceDetailsVisible && (
          <Route
            path="/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/(booking|cancelled)/:bookingId?"
            render={route => (
              <BookingContainer extraClassName="with-header" {...route} />
            )}
          />
        )}
        {recommendation && (
          <Fragment>
            <VersoContainer
              recommendation={recommendation}
              extraClassName="with-header"
              forceDetailsVisible={forceDetailsVisible}
            />
            <RectoContainer
              recommendation={recommendation}
              areDetailsVisible={forceDetailsVisible}
              extraClassName="with-header"
              position="current"
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
  recommendation: PropTypes.object,
}
