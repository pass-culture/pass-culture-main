import { fireEvent, screen } from '@testing-library/react'
import { vi } from 'vitest'

import { VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Venue, type VenueProps } from './Venue'

const logEventMock = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: logEventMock }),
}))

const renderVenue = (
  props: VenueProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<Venue {...props} />, options)
}

describe('<Venues />', () => {
  const offererId = 12
  const venueId = 1
  const baseProps: VenueProps = {
    offerer: { ...defaultGetOffererResponseModel, id: offererId },
    venue: {
      ...defaultGetOffererVenueResponseModel,
      id: venueId,
      name: 'Mon Lieu',
      publicName: 'My venue',
      isVirtual: false,
    },
    isFirstVenue: false,
  }

  it('should display edition venue link', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        isVirtual: false,
      },
    }

    renderVenue(props)

    expect(
      screen.getByRole('link', { name: `Gérer la page de My venue` })
    ).toHaveAttribute('href', `/structures/${offererId}/lieux/${venueId}`)
  })

  it('should not display dms timeline link if venue has no dms application', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        collectiveDmsApplications: [],
      },
    }

    renderVenue(props)

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).toBeFalsy()
  })

  it('should display API tag if venue has at least one provider', async () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        hasVenueProviders: true,
      },
    }

    renderVenue(props)

    const apiTag = await screen.findByText('API')
    expect(apiTag).toBeInTheDocument()
  })

  it('should reset open state when venue offer steps visibility changes', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        hasCreatedOffer: false,
      },
    }

    const { rerender } = renderWithProviders(<Venue {...props} />)

    fireEvent.click(
      screen.getByRole('button', { name: 'Masquer les statistiquesMy venue' })
    )

    expect(
      screen.getByRole('img', { name: 'Afficher les statistiques' })
    ).toBeInTheDocument()

    rerender(
      <Venue
        {...props}
        venue={{
          ...props.venue,
          hasCreatedOffer: true,
          collectiveDmsApplications: [],
        }}
      />
    )

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('should update internal offerer id tracking when offerer changes', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        hasCreatedOffer: false,
      },
    }

    const { rerender } = renderWithProviders(<Venue {...props} />)

    expect(screen.getByRole('button')).toBeInTheDocument()

    rerender(
      <Venue
        {...props}
        offerer={{ ...props.offerer!, id: props.offerer!.id + 1 }}
      />
    )

    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('should toggle accordion and log analytics event', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        hasCreatedOffer: false,
        isVirtual: false,
      },
    }

    renderVenue(props)

    expect(
      screen.getByRole('img', { name: 'Masquer les statistiques' })
    ).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button'))

    expect(
      screen.getByRole('img', { name: 'Afficher les statistiques' })
    ).toBeInTheDocument()
    expect(logEventMock).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
      { venue_id: venueId }
    )
  })

  it('should render non-toggle header when steps should not be shown', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        collectiveDmsApplications: [],
        hasCreatedOffer: true,
      },
    }

    renderVenue(props)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(screen.getByTestId(`venue-name-div-${venueId}`)).toBeInTheDocument()
  })

  it('should display virtual venue name', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        isVirtual: true,
      },
    }

    renderVenue(props)

    expect(screen.getByText('Offres numériques')).toBeInTheDocument()
  })

  it('should log analytics when clicking manage page link', () => {
    const props = {
      ...baseProps,
      venue: {
        ...baseProps.venue,
        isVirtual: false,
      },
    }

    renderVenue(props)

    fireEvent.click(
      screen.getByRole('link', { name: `Gérer la page de My venue` })
    )

    expect(logEventMock).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
      { venue_id: venueId }
    )
  })
})
