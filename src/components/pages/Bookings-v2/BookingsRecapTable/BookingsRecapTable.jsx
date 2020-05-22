import React, { Component } from 'react'
import PropTypes from 'prop-types'
import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingDateCell'
import BookingStatusCell from './CellsFormatter/BookingStatusCell'
import BookingTokenCell from './CellsFormatter/BookingTokenCell'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import Header from './Header/Header'
import BookingIsDuoCell from './CellsFormatter/BookingIsDuoCell'
import { NB_BOOKINGS_PER_PAGE } from './NB_BOOKINGS_PER_PAGE'
import TableFrame from './Table/TableFrame'
import BookingsRecapFilters from './Filters/BookingsRecapFilters'


class BookingsRecapTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingsRecapFiltered: props.bookingsRecap,
      columns: [
        {
          id: 1,
          headerTitle: "Nom de l'offre",
          accessor: 'stock',
          Cell: ({ value }) => <BookingOfferCell offer={value} />,
          className: 'td-offer-name',
        },
        {
          id: 2,
          headerTitle: '',
          accessor: 'booking_is_duo',
          Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
          className: 'td-booking-duo',
        },
        {
          id: 3,
          headerTitle: 'Bénéficiaire',
          accessor: 'beneficiary',
          Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
          className: 'td-beneficiary',
        },
        {
          id: 4,
          headerTitle: 'Réservation',
          accessor: 'booking_date',
          Cell: ({ value }) => <BookingDateCell bookingDate={value} />,
          className: 'td-booking-date',
        },
        {
          id: 5,
          headerTitle: 'Contremarque',
          accessor: 'booking_token',
          Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
          className: 'td-booking-token',
        },
        {
          id: 6,
          headerTitle: 'Statut',
          accessor: 'booking_status',
          Cell: ({ value }) => <BookingStatusCell bookingStatus={value} />,
          className: 'td-booking-status',
        },
      ],
      currentPage: 0,
      filters: {
        offerName: null,
        eventDate: null,
      },
      nbBookings: props.nbBookings,
    }
  }

  shouldComponentUpdate() {
    return true
  }

  componentDidUpdate(prevProps) {
    if (prevProps.bookingsRecap.length !== this.props.bookingsRecap.length){
      this.applyFilters()
    }
  }

  updateCurrentPage = currentPage => {
    this.setState({
      currentPage: currentPage,
    })
  }

  setFilters = filters => {
    this.setState({ filters: filters })
    this.applyFilters()
  }

  applyFilters = () => {
    const {filters} = this.state
    const {bookingsRecap} = this.props

    const bookingsRecapFiltered = filters.offerName ?
      bookingsRecap.filter(
        booking => booking.stock.offer_name.toLowerCase().includes(filters.offerName)
      ) : bookingsRecap

    this.setState({bookingsRecapFiltered: bookingsRecapFiltered})
    console.log("NB BOOKINGS", bookingsRecapFiltered.length)
  }

  render() {
    const { bookingsRecap, isLoading } = this.props
    const { bookingsRecapFiltered, columns, currentPage } = this.state

    return (
      <div>
        <BookingsRecapFilters
          setFilters={this.setFilters}
          bookingsRecap={bookingsRecap}
          filters={{ 'offer_name': true, 'booking_date': false }}
        />
        <Header isLoading={isLoading}
                nbBookings={bookingsRecapFiltered.length}
        />
        <TableFrame
          columns={columns}
          currentPage={currentPage}
          data={bookingsRecapFiltered}
          nbBookings={bookingsRecapFiltered.length}
          nbBookingsPerPage={NB_BOOKINGS_PER_PAGE}
          updateCurrentPage={this.updateCurrentPage}
        />
      </div>
    )
  }
}

BookingsRecapTable.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  nbBookings: PropTypes.number.isRequired,
}

export default BookingsRecapTable
