import { requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Recto from '../../Recto'
import Verso from '../../verso'
import { recommendationNormalizer } from '../../../utils/normalizers'

class SearchDetails extends Component {
  constructor() {
    super()
    this.state = { isLoading: true }
  }

  componentDidMount() {
    this.handleRequestData()
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

  handleRequestData = () => {
    const { dispatch, match } = this.props
    const {
      params: { mediationId, offerId },
    } = match

    let path = `recommendations/offers/${offerId}`
    if (mediationId) {
      path = `${path}?mediationId=${mediationId}`
    }

    this.setState({ isLoading: true }, () =>
      dispatch(
        requestData('GET', path, {
          handleSuccess: (state, action) => {
            this.handleClickRecommendation(action.data)
            this.setState({ isLoading: false })
          },
          normalizer: recommendationNormalizer,
        })
      )
    )


  }

  render() {
    const { isLoading } = this.state
    if (isLoading) {
      return null
    }
    return (
      <Fragment>
        <Verso forceDetailsVisible className="with-header" />
        <Recto position="current" />
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
