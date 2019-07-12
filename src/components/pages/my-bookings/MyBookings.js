import PropTypes from 'prop-types'
import React, { Component } from 'react'

import LoaderContainer from '../../layout/Loader/LoaderContainer'
import MyBookingContainer from './MyBookingContainer'
import NavigationFooter from '../../layout/NavigationFooter'
import NoBookings from './NoBookings'
import PageHeader from '../../layout/Header/PageHeader'

class MyBookings extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
      isEmpty: false,
      isLoading: true,
    }
  }

  componentDidMount = () => {
    const { getMyBookings } = this.props

    getMyBookings(this.handleFail, this.handleSuccess)
  }

  build = myBookings => (
    <ul>
      {myBookings.map(myBooking => (
        <MyBookingContainer
          booking={myBooking}
          key={myBooking.id}
        />
      ))}
    </ul>
  )

  handleFail = () => {
    this.setState({
      hasError: true,
      isLoading: true,
    })
  }

  handleSuccess = (state, action) => {
    this.setState({
      isEmpty: action.payload.data.length === 0,
      isLoading: false,
    })
  }

  render() {
    const { soonBookings, myBookings } = this.props
    const { isEmpty, isLoading, hasError } = this.state

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <div className="my-bookings">
        <PageHeader title="Mes réservations" />
        <main className={isEmpty ? 'mb-main mb-no-bookings' : 'mb-main'}>
          {isEmpty && <NoBookings />}

          {soonBookings.length > 0 && (
            <section className="mb-section">
              <header className="mb-header">{'C’est bientôt !'}</header>
              {this.build(soonBookings)}
            </section>
          )}

          {myBookings.length > 0 && (
            <section className="mb-section">
              <header className="mb-header">{'Réservations'}</header>
              {this.build(myBookings)}
            </section>
          )}
        </main>
        <NavigationFooter
          className="dotted-top-white"
          theme="purple"
        />
      </div>
    )
  }
}

MyBookings.propTypes = {
  getMyBookings: PropTypes.func.isRequired,
  myBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  soonBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default MyBookings
