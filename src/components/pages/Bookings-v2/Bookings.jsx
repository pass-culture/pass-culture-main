import React, {PureComponent} from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsTable from './BookingsTable/BookingsTable'

class Bookings extends PureComponent {
  constructor(props){
    super(props)
    this.state = {bookingsRecap: []}
  }

  componentDidMount() {
    const { requestGetAllBookingsRecap } = this.props
    requestGetAllBookingsRecap(this.handleSuccess, this.handleFailure)
  }

  handleSuccess = (state, action = {}) => {
    const {payload = {}} = action
    const {data} = payload
    this.setState({bookingsRecap: data})
  }

  handleFailure = () => {
    console.log("HandleFailure")
  }

  render() {
    const { bookingsRecap } = this.state
    return (
      <Main name="bookings-v2">
        <Titles title="Réservations V2" />
        <BookingsTable bookingsRecap={bookingsRecap} />
      </Main>
    )
  }
}

export default Bookings
