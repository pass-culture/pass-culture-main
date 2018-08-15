import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import currentRecommendationSelector from '../selectors/currentRecommendation'

class BookingCard extends React.PureComponent {
  componentWillMount() {
    console.log('BookingCard ---> componentWillMount')
  }

  componentWillUnmount() {
    console.log('BookingCard ---> componentWillUnmount')
  }

  render() {
    console.log('BookingCard ---> render')
    const { recommendation } = this.props
    return (
      <div id="booking-card">
        {console.log('recommendation', recommendation)}
      </div>
    )
  }
}

BookingCard.defaultProps = {
  recommendation: null,
}

BookingCard.propTypes = {
  recommendation: PropTypes.object,
}

const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  return {
    recommendation,
  }
}

export default connect(mapStateToProps)(BookingCard)
