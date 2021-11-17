import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'
import { toast } from 'react-toastify'

import isDetailsView from '../../../utils/isDetailsView'
import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import RectoContainer from '../Recto/RectoContainer'
import VersoContainer from '../Verso/VersoContainer'
import { dehumanizeId } from '../../../utils/dehumanizeId/dehumanizeId'
import { WEBAPP_V2_URL } from '../../../utils/config'

class Details extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      isDetailsView: false,
    }
  }

  componentDidMount() {
    const { getOfferById, match } = this.props
    this.v2RedirectCheck()
    this.handleSetIsDetailsView()
    const { params } = match
    const { offerId } = params
    getOfferById(offerId)
  }

  componentDidUpdate() {
    this.handleSetIsDetailsView()
  }

  componentWillUnmount() {
    this.v2RedirectCheck(true)
  }

  handleSetIsDetailsView = () => {
    const { match } = this.props
    this.setState({
      isDetailsView: isDetailsView(match),
    })
  }

  v2Redirect = (url, message, isInstantRedirect) => {
    if (isInstantRedirect) {
      window.location.replace(url)
      return
    }
    const toastDurationInMs = 5000
    const offsetInMs = 300
    toast.error(message)
    setTimeout(() => {
      window.location.replace(url)
    }, toastDurationInMs + offsetInMs)
  }

  v2RedirectCheck = isInstantRedirect => {
    const { webAppV2Enabled, match, trackV1toV2HomeRedirect, trackV1toV2OfferRedirect } = this.props
    if (webAppV2Enabled) {
      let redirected = false
      try {
        const dehumanizedOfferId = dehumanizeId(match.params.offerId)
        if (dehumanizedOfferId && dehumanizedOfferId > 0) {
          const offerV2Url = `${WEBAPP_V2_URL}/offre/${dehumanizedOfferId}`
          redirected = true
          trackV1toV2OfferRedirect({ url: offerV2Url, offerId: dehumanizedOfferId })
          this.v2Redirect(
            offerV2Url,
            `Ce lien n'est plus à jour, tu vas être redirigé vers le nouveau site du pass Culture, pense à mettre à jour tes favoris.`,
            isInstantRedirect
          )
        }
      } finally {
        if (!redirected) {
          trackV1toV2HomeRedirect({
            url: WEBAPP_V2_URL,
            offerId: match.params && match.params.offerId,
          })
          this.v2Redirect(
            WEBAPP_V2_URL,
            `Ce lien n'est plus à jour, tu vas être redirigé vers le nouveau site du pass Culture.`,
            isInstantRedirect
          )
        }
      }
    }
  }

  renderBookingOrCancellation = route => {
    const { cancelView } = this.props

    return cancelView ? this.renderBookingCancellation(route) : this.renderBooking(route)
  }

  renderBookingCancellation = route => {
    const { withHeader } = this.props
    return (
      <BookingCancellationContainer
        extraClassName={`${withHeader ? 'with-header' : ''}`}
        {...route}
      />
    )
  }

  renderBooking = route => {
    const { withHeader } = this.props
    return (
      <BookingContainer
        extraClassName={`${withHeader ? 'with-header' : ''}`}
        {...route}
      />
    )
  }

  render() {
    const { bookingPath, withHeader } = this.props
    const { isDetailsView } = this.state

    return (
      <Fragment>
        <Route
          path={bookingPath}
          render={this.renderBookingOrCancellation}
          sensitive
        />
        <VersoContainer
          areDetailsVisible={isDetailsView}
          extraClassName={`${withHeader ? 'with-header' : ''}`}
        />
        {isDetailsView && <RectoContainer areDetailsVisible />}
      </Fragment>
    )
  }
}

Details.defaultProps = {
  bookingPath: '',
  cancelView: false,
  webAppV2Enabled: false,
  withHeader: true,
}

Details.propTypes = {
  bookingPath: PropTypes.string,
  cancelView: PropTypes.bool,
  getOfferById: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
      offerId: PropTypes.string,
    }),
  }).isRequired,
  trackV1toV2HomeRedirect: PropTypes.func.isRequired,
  trackV1toV2OfferRedirect: PropTypes.func.isRequired,
  webAppV2Enabled: PropTypes.bool,
  withHeader: PropTypes.bool,
}

export default Details
