import type { Location } from 'history'
import React, { useCallback, useState, useMemo } from 'react'

import { BookingRecapResponseModel } from 'api/v1/gen'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { TPreFilters } from 'core/Bookings'

import BookingsRecapTable from '../../components/pages/Bookings/BookingsRecapTable/BookingsRecapTable'
import ChoosePreFiltersMessage from '../../components/pages/Bookings/ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import NoBookingMessage from '../../components/pages/Bookings/NoBookingMessage'
import NoBookingsForPreFiltersMessage from '../../components/pages/Bookings/NoBookingsForPreFiltersMessage/NoBookingsForPreFiltersMessage'
import { DEFAULT_PRE_FILTERS } from '../../components/pages/Bookings/PreFilters/_constants'
import PreFilters from '../../components/pages/Bookings/PreFilters/PreFilters'

interface IBookingsProps {
  bookingsRecap: BookingRecapResponseModel[]
  downloadBookingsCSV: (filters: TPreFilters) => void
  hasBooking: boolean
  isBookingFiltersActive: boolean
  isDownloadingCSV: boolean
  isTableLoading: boolean
  loadBookingsRecap: (filters: TPreFilters) => void
  locationState: Location['state']
  setWereBookingsRequested: (wereBookingsRequested: boolean) => void
  venueId?: string
  wereBookingsRequested: boolean
}

const Bookings = ({
  bookingsRecap,
  downloadBookingsCSV,
  hasBooking,
  isBookingFiltersActive,
  isDownloadingCSV,
  isTableLoading,
  loadBookingsRecap,
  locationState,
  setWereBookingsRequested,
  venueId,
  wereBookingsRequested,
}: IBookingsProps): JSX.Element => {
  const [appliedPreFilters, setAppliedPreFilters] = useState<TPreFilters>({
    bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
    bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
    bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
    offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
    offerVenueId: venueId || DEFAULT_PRE_FILTERS.offerVenueId,
    offerType: DEFAULT_PRE_FILTERS.offerType,
  })

  const werePreFiltersCustomized = useMemo(() => {
    return (
      appliedPreFilters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId ||
      appliedPreFilters.bookingBeginningDate !==
        DEFAULT_PRE_FILTERS.bookingBeginningDate ||
      appliedPreFilters.bookingEndingDate !==
        DEFAULT_PRE_FILTERS.bookingEndingDate ||
      appliedPreFilters.bookingStatusFilter !==
        DEFAULT_PRE_FILTERS.bookingStatusFilter ||
      appliedPreFilters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate
    )
  }, [
    appliedPreFilters.bookingStatusFilter,
    appliedPreFilters.bookingBeginningDate,
    appliedPreFilters.bookingEndingDate,
    appliedPreFilters.offerEventDate,
    appliedPreFilters.offerVenueId,
  ])

  const resetPreFilters = useCallback(() => {
    setWereBookingsRequested(false)
    setAppliedPreFilters({ ...DEFAULT_PRE_FILTERS })
  }, [setWereBookingsRequested])

  const applyPreFilters = (filters: TPreFilters) => {
    setAppliedPreFilters(filters)
    loadBookingsRecap(filters)
  }

  return (
    <div className="bookings-page">
      <PageTitle title="Vos réservations" />
      <Titles title="Réservations" />
      <h2 className="br-title">Affichage des réservations</h2>
      {werePreFiltersCustomized && (
        <button
          className="tertiary-button reset-filters-link"
          onClick={resetPreFilters}
          type="button"
        >
          Réinitialiser les filtres
        </button>
      )}
      <PreFilters
        appliedPreFilters={appliedPreFilters}
        applyPreFilters={applyPreFilters}
        downloadBookingsCSV={downloadBookingsCSV}
        hasResult={bookingsRecap.length > 0}
        isBookingFiltersActive={isBookingFiltersActive}
        isDownloadingCSV={isDownloadingCSV}
        isFiltersDisabled={!hasBooking}
        isTableLoading={isTableLoading}
        wereBookingsRequested={wereBookingsRequested}
      />
      {wereBookingsRequested ? (
        bookingsRecap.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            isBookingFiltersActive={isBookingFiltersActive}
            isLoading={isTableLoading}
            locationState={locationState}
          />
        ) : isTableLoading ? (
          <Spinner />
        ) : (
          <NoBookingsForPreFiltersMessage resetPreFilters={resetPreFilters} />
        )
      ) : hasBooking ? (
        <ChoosePreFiltersMessage />
      ) : (
        <NoBookingMessage />
      )}
    </div>
  )
}

export default Bookings
