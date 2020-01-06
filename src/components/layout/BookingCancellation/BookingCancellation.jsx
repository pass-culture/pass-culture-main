import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { Transition } from 'react-transition-group'
import BookingCancel from './BookingCancel/BookingCancel'
import BookingHeader from '../Booking/BookingHeader/BookingHeader'

class BookingCancellation extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      mounted: false,
    }
  }

  componentDidMount() {
    this.handleSetMounted(true)
  }

  componentWillUnmount() {
    this.handleSetMounted(false)
  }

  handleSetMounted = mounted => {
    this.setState({ mounted })
  }

  handleReturnToDetails = () => {
    const { match, history } = this.props
    const { url } = match
    const detailsUrl = url.split(/\/reservation(\/|$|\/$)/)[0]
    history.replace(detailsUrl)
  }

  render() {
    const { booking, extraClassName, offer } = this.props
    const { mounted } = this.state
    const { isEvent } = offer || {}

    return (
      <Transition
        in={mounted}
        timeout={0}
      >
        {state => (
          <div
            className={`is-overlay is-clipped flex-rows ${extraClassName} ${state}`}
            id="booking-card"
          >
            <div className="main flex-rows flex-1 scroll-y">
              <BookingHeader offer={offer} />
              <div className="mosaic-background content flex-1 flex-center">
                <div className="flex-rows">
                  <BookingCancel
                    booking={booking}
                    isEvent={isEvent}
                  />
                </div>
              </div>
            </div>
            <div className="form-footer flex-columns flex-0 flex-center">
              <button
                className="text-center my5"
                id="booking-cancellation-confirmation-button"
                onClick={this.handleReturnToDetails}
                type="button"
              >
                {'OK'}
              </button>
            </div>
          </div>
        )}
      </Transition>
    )
  }
}

BookingCancellation.defaultProps = {
  booking: null,
  extraClassName: '',
  offer: null,
}

BookingCancellation.propTypes = {
  booking: PropTypes.shape({
    amount: PropTypes.number,
  }),
  extraClassName: PropTypes.string,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape({
    url: PropTypes.string.isRequired,
  }).isRequired,
  offer: PropTypes.shape({
    isEvent: PropTypes.bool,
    name: PropTypes.string,
    venue: PropTypes.shape(),
  }),
}

export default BookingCancellation
