import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { Route, withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import get from 'lodash.get'

import BookingContainer from '../../booking/BookingContainer'
import { recommendationNormalizer } from '../../../utils/normalizers'
import RectoContainer from '../../recto/RectoContainer'
import { selectCurrentSearchRecommendation } from '../../../selectors'
import VersoContainer from '../../verso/VersoContainer'

export class SearchDetails extends Component {
  constructor() {
    super()
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
  match: PropTypes.object.isRequired,
  recommendation: PropTypes.object,
}

function mapStateToProps(state, ownProps) {
  const { match } = ownProps
  const offerId = get(match, 'params.offerId')
  const mediationId = get(match, 'params.mediationId')
  const recommendation = selectCurrentSearchRecommendation(
    state,
    offerId,
    mediationId
  )

  return { recommendation }
}

export const SearchDetailsContainer = compose(
  withRouter,
  connect(mapStateToProps)
)(SearchDetails)
