import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, describe, expect } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import * as useMediaQuery from '@/commons/hooks/useMediaQuery'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SAVED_PARTNER_PAGE_VENUE_ID_KEYS } from '@/commons/utils/savedPartnerPageVenueId'

import { SideNavLinks } from './SideNavLinks'

const selectCurrentOfferer = vi.hoisted(() => vi.fn())
vi.mock('@/commons/store/offerer/selectors', async (importOriginal) => ({
  ...(await importOriginal()),
  selectCurrentOfferer,
}))

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<SideNavLinks isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

describe('SideNavLinks', () => {
  it('should not have accessibility violations', async () => {
    const { container } = renderSideNavLinks()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should toggle individual section on individual section button click', async () => {
    renderSideNavLinks()

    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(
      screen.queryByRole('link', { name: 'Guichet' })
    ).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(screen.getByRole('link', { name: 'Guichet' })).toBeInTheDocument()
  })

  it('should toggle collective section on collective section button click', async () => {
    renderSideNavLinks()

    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))
    expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(1)
    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))
    expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(2)
  })

  it('should show template and bookable offers links and hide bookings link in collective offer section link when FF is enabled', async () => {
    renderSideNavLinks({
      features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'],
    })

    // close individual section
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))

    expect(
      screen.getByRole('link', { name: 'Offres vitrines' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Offres réservables' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('link', { name: 'Réservations' })
    ).not.toBeInTheDocument()
  })

  it('should not show template offers link in collective offer section link when FF is disabled', async () => {
    renderSideNavLinks()

    // close individual section
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))

    expect(
      screen.queryByRole('link', { name: 'Offres vitrines' })
    ).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Offres' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Réservations' })
    ).toBeInTheDocument()
  })

  describe('when the user has a partner page', () => {
    const linkLabel = 'Page sur l’application'

    const mockedPartnerPageVenue = {
      ...defaultGetOffererVenueResponseModel,
      hasCreatedOffer: true,
      isPermanent: true,
      hasPartnerPage: true,
    }

    // We assume that the first venue is the one that has no partner page.
    const mockedNotAPartnerPageVenueId = 0
    const mockedManagedVenuesLength = 10
    const mockedManagedVenues = new Array(mockedManagedVenuesLength)
      .fill(mockedPartnerPageVenue)
      .map((_, index) => ({
        ...mockedPartnerPageVenue,
        id: index,
        // Normally, hasPartnerPage is false if either hasCreatedOffer or isPermanent is false.
        // We dont need those values here.
        hasPartnerPage: index !== mockedNotAPartnerPageVenueId,
      }))

    const offerer = currentOffererFactory()

    beforeEach(() => {
      selectCurrentOfferer.mockReturnValue({
        ...defaultGetOffererResponseModel,
        hasPartnerPage: true,
        managedVenues: mockedManagedVenues,
      })
    })

    afterEach(() => {
      localStorage.clear()
    })

    it('should always display a "Page sur l’application" link', async () => {
      renderSideNavLinks({ storeOverrides: { offerer } })

      const link = await screen.findByRole('link', { name: linkLabel })
      expect(link).toBeInTheDocument()
    })

    it('should display a partner link with redux store selected venue if available', async () => {
      // We assume that the last venue is the one that is stored.
      // This should be overtaken by the redux store selected venue id.
      const locallyStoredVenueId = mockedManagedVenuesLength - 1
      const reduxStoreSelectedVenueId = mockedManagedVenuesLength - 2

      localStorage.setItem(
        SAVED_PARTNER_PAGE_VENUE_ID_KEYS,
        JSON.stringify({
          [offerer.currentOfferer?.id as number]:
            locallyStoredVenueId.toString(),
        })
      )

      renderSideNavLinks({
        storeOverrides: {
          nav: {
            isIndividualSectionOpen: true,
            isCollectiveSectionOpen: true,
            selectedPartnerPageId: reduxStoreSelectedVenueId.toString(),
          },
          offerer,
        },
      })

      const link = await screen.findByRole('link', { name: linkLabel })
      expect(link).toHaveAttribute(
        'href',
        `/structures/${offerer.currentOfferer?.id}/lieux/${reduxStoreSelectedVenueId.toString()}/page-partenaire`
      )
    })

    it('should display a partner link with previously selected / locally stored venue if available & still relevant', async () => {
      // We assume that the last venue is the one that is stored.
      const locallyStoredVenueId = mockedManagedVenuesLength - 1

      localStorage.setItem(
        SAVED_PARTNER_PAGE_VENUE_ID_KEYS,
        JSON.stringify({
          [offerer.currentOfferer?.id as number]:
            locallyStoredVenueId.toString(),
        })
      )

      renderSideNavLinks({ storeOverrides: { offerer } })

      const link = await screen.findByRole('link', { name: linkLabel })
      expect(link).toHaveAttribute(
        'href',
        `/structures/${offerer.currentOfferer?.id}/lieux/${locallyStoredVenueId.toString()}/page-partenaire`
      )
    })

    it('should display a partner link with 1st venue selected as default otherwise', async () => {
      // We assume that the locally stored venue is the venue that has no partner page,
      // to test a case where the stored venue was a partner page but is not anymore.
      const locallyStoredVenueId = mockedNotAPartnerPageVenueId
      const fallbackVenueId = mockedManagedVenues.find(
        (v) => v.hasPartnerPage
      )?.id

      localStorage.setItem(
        SAVED_PARTNER_PAGE_VENUE_ID_KEYS,
        JSON.stringify({
          [offerer.currentOfferer?.id as number]:
            locallyStoredVenueId.toString(),
        })
      )

      renderSideNavLinks({ storeOverrides: { offerer } })

      const link = await screen.findByRole('link', { name: linkLabel })
      expect(link).toHaveAttribute(
        'href',
        `/structures/${offerer.currentOfferer?.id}/lieux/${fallbackVenueId}/page-partenaire`
      )
    })
  })

  it('should not display partner link if user as no partner page', () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      hasPartnerPage: false,
    })

    renderSideNavLinks({
      user: sharedCurrentUserFactory(),
    })

    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
  })

  it('should not display create offre button if offerer is not validated', () => {
    selectCurrentOfferer.mockReturnValue(null)

    renderSideNavLinks({
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
        },
        offerer: currentOffererFactory(),
      },
      user: sharedCurrentUserFactory(),
    })

    expect(
      screen.queryByRole('link', { name: 'Créer une offre' })
    ).not.toBeInTheDocument()
  })

  describe('on large height devices', () => {
    it('should not collapse menus', () => {
      vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

      renderSideNavLinks()

      const individualAccordionButton = screen.getByRole('button', {
        name: 'Individuel',
      })
      expect(individualAccordionButton).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Guichet' })).toBeInTheDocument()
    })

    describe('when window is resized to have a smaller height', () => {
      it('should collapse individual section when location path doesnt match an individual page', () => {
        vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

        const { rerender } = renderSideNavLinks({
          initialRouterEntries: ['/offres/collectives'],
        })

        expect(
          screen.getByRole('link', { name: 'Guichet' })
        ).toBeInTheDocument()

        vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(true)
        rerender(<SideNavLinks isLateralPanelOpen={true} />)

        expect(
          screen.queryByRole('link', { name: 'Guichet' })
        ).not.toBeInTheDocument()
      })

      it('should collapse collective section when location path doesnt match a collective page', () => {
        vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

        const { rerender } = renderSideNavLinks({
          initialRouterEntries: ['/offres'],
        })

        expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(2)

        vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(true)
        rerender(<SideNavLinks isLateralPanelOpen={true} />)

        expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(1)
      })

      it('should collapse both section when location path doesnt match any page', () => {
        vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

        const { rerender } = renderSideNavLinks({
          initialRouterEntries: ['/'],
        })

        expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(2)

        vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(true)
        rerender(<SideNavLinks isLateralPanelOpen={true} />)

        expect(
          screen.queryByRole('link', { name: 'Offres' })
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('on small height devices', () => {
    beforeEach(() => {
      vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(true)
    })

    it('should collapse menus', () => {
      renderSideNavLinks()

      const individualAccordionButton = screen.getByRole('button', {
        name: 'Individuel',
      })
      expect(individualAccordionButton).toBeInTheDocument()
      expect(
        screen.queryByRole('link', { name: 'Guichet' })
      ).not.toBeInTheDocument()
    })

    it('should collapse one menu at a time', async () => {
      renderSideNavLinks()

      const individualAccordionButton = screen.getByRole('button', {
        name: 'Individuel',
      })
      const collectiveAccordionButton = screen.getByRole('button', {
        name: 'Collectif',
      })

      await userEvent.click(individualAccordionButton)
      expect(
        screen.queryByRole('link', { name: 'Guichet' })
      ).toBeInTheDocument()
      await userEvent.click(collectiveAccordionButton)
      expect(
        screen.queryByRole('link', { name: 'Guichet' })
      ).not.toBeInTheDocument()
    })
  })

  it('should show a create offer dropdown button with individual and collective choices if the FF WIP_ENABLE_NEW_OFFER_CREATION_FLOW is enabled', async () => {
    selectCurrentOfferer.mockReturnValue({
      ...defaultGetOffererResponseModel,
      isValidated: true,
    })

    renderSideNavLinks({
      storeOverrides: {
        offerer: currentOffererFactory(),
      },
      features: ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'],
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Créer une offre' })
    )

    expect(screen.getByRole('menuitem', { name: 'Pour le grand public' }))
    expect(screen.getByRole('menuitem', { name: 'Pour les groupes scolaires' }))
  })
})
