import { requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { Route, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Booking from '../../booking'
import Recto from '../../Recto'
import Verso from '../../verso'
import { recommendationNormalizer } from '../../../utils/normalizers'

class SearchDetails extends Component {
  constructor() {
    super()
    this.state = { forceDetailsVisible: false }
  }

  componentDidMount() {
    this.handleRequestData()
    // setTimeout(this.handleForceDetailsVisible)
  }

  handleClickRecommendation = recommendation => {
    if (recommendation.isClicked) {
      return
    }

    const { dispatch } = this.props
    const options = {
      body: { isClicked: true },
      key: 'recommendations',
    }

    const path = `recommendations/${recommendation.id}`

    dispatch(requestData('PATCH', path, options))
  }

  handleRequestSuccess = (state, action) => {
    this.handleClickRecommendation(action.data)
    this.handleForceDetailsVisible()
  }

  handleRequestData = () => {
    const { dispatch, match } = this.props
    const {
      params: { mediationId, offerId },
    } = match

    let path = `recommendations/offers/${offerId}`
    if (mediationId) {
      path = `${path}?mediationId=${mediationId}`
    }

    dispatch(
      requestData('GET', path, {
        handleSuccess: this.handleRequestSuccess,
        normalizer: recommendationNormalizer,
      })
    )
  }

  handleForceDetailsVisible = () => {
    this.setState({ forceDetailsVisible: true })
  }

  render() {
    const { forceDetailsVisible } = this.state
    return (
      <Fragment>
        {forceDetailsVisible && (
          <Route
            path="/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/(booking|cancelled)/:bookingId?"
            render={route => (
              <Booking extraClassName="with-header" {...route} />
            )}
          />
        )}
        <Verso
          extraClassName="with-header"
          forceDetailsVisible={forceDetailsVisible}
        />
        <Recto
          areDetailsVisible={forceDetailsVisible}
          extraClassName="with-header"
          position="current"
        />
      </Fragment>
    )
  }
}

SearchDetails.propTypes = {
  dispatch: PropTypes.func.isRequired,
  match: PropTypes.object.isRequired,
}

export default compose(
  withRouter,
  connect()
)(SearchDetails)
