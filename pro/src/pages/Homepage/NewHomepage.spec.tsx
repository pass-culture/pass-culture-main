import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { DMSApplicationstatus } from '@/apiClient/v1/models/DMSApplicationstatus'
import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererVenueResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { PartnerLayout } from '@/layouts/PartnerLayout/PartnerLayout'

import * as utils from './commons/utils'
import { NewHomepage } from './NewHomepage'

vi.mock('@/components/CollectiveDmsTimeline/CollectiveDmsTimeline', () => ({
  CollectiveDmsTimeline: () => <div>timeline DMS</div>,
}))

vi.mock('./components/PartnerPageCard/PartnerPageCard', () => ({
  PartnerPageCard: () => <div>page partenaire</div>,
}))

vi.mock('./components/IncomeCard/IncomeCard', () => ({
  IncomeCard: () => <div>Remboursement</div>,
}))

vi.mock('./components/VenueValidationBanner/VenueValidationBanner', () => ({
  VenueValidationBanner: () => <div>Homologation</div>,
}))

const newHomepageRoutes = [
  {
    path: '/',
    Component: PartnerLayout,
    children: [
      {
        path: 'accueil',
        element: <NewHomepage />,
        handle: { title: 'Espace acteurs culturels' },
      },
    ],
  },
]

const renderNewHomepage = (
  venueOverrides?: Partial<GetVenueResponseModel>,
  options?: RenderWithProvidersOptions
) => {
  const user = sharedCurrentUserFactory()
  const defaultVenue = makeGetVenueResponseModel({
    id: 1,
    managingOffererId: 1,
    name: 'Club Dorothy',
  })
  const { storeOverrides, ...restOptions } = options ?? {}
  return renderWithProviders(null, {
    features: ['WIP_ENABLE_NEW_PRO_HOME', 'WIP_SWITCH_VENUE'],
    routes: newHomepageRoutes,
    initialRouterEntries: ['/accueil'],
    user,
    ...restOptions,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: {
          ...defaultVenue,
          ...venueOverrides,
        },
      },
      ...storeOverrides,
    },
  })
}

describe('NewHomepage', () => {
  beforeEach(() => {
    vi.mock('@/app/AppRouter/utils', async () => ({
      ...(await vi.importActual('@/app/AppRouter/utils')),
      isNewHomepageEnabled: () => true,
    }))
  })

  it('should display the selected venue public name in the title', () => {
    renderNewHomepage()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Votre espace Nom public de la structure'
    )
  })

  describe('venue validation banner', () => {
    it('should not be displayed when the venue is validated', () => {
      renderNewHomepage({
        ...defaultGetOffererVenueResponseModel,
        isValidated: true,
      })

      expect(screen.queryByText('Homologation')).not.toBeInTheDocument()
    })

    it('should be displayed if the venue is not validated', () => {
      renderNewHomepage({
        ...defaultGetOffererVenueResponseModel,
        isValidated: false,
      })

      expect(screen.getByText('Homologation')).toBeVisible()
    })
  })

  describe('Tabs', () => {
    it.each`
      scenario | allowedOnAdage | hasNonDraftOffers | hasCollectiveDMS | shouldDisplayTabs
      ${1}     | ${true}        | ${true}           | ${true}          | ${true}
      ${2}     | ${true}        | ${true}           | ${false}         | ${true}
      ${3}     | ${false}       | ${true}           | ${true}          | ${true}
      ${4}     | ${false}       | ${true}           | ${false}         | ${false}
      ${5}     | ${false}       | ${false}          | ${true}          | ${false}
      ${6}     | ${true}        | ${false}          | ${false}         | ${false}
    `(
      'should display tabs: $shouldDisplayTabs on scenario $scenario',
      ({
        allowedOnAdage,
        hasNonDraftOffers,
        hasCollectiveDMS,
        shouldDisplayTabs,
      }) => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          allowedOnAdage,
          hasNonDraftOffers,
          collectiveDmsApplications: hasCollectiveDMS
            ? [defaultDMSApplicationForEAC]
            : undefined,
        })

        if (shouldDisplayTabs) {
          expect(screen.getByRole('tablist')).toBeVisible()
        } else {
          expect(screen.queryByRole('tablist')).not.toBeInTheDocument()
        }
      }
    )

    it('should render without accessibility violation', async () => {
      const { container } = renderNewHomepage({
        ...defaultGetOffererVenueResponseModel,
        allowedOnAdage: true,
        hasNonDraftOffers: true,
      })

      expect(
        await axe(container, {
          rules: { 'aria-allowed-attr': { enabled: false } },
        })
      ).toHaveNoViolations()
    })

    it('should display the corresponding panel when click on a given tab', async () => {
      const user = userEvent.setup()
      renderNewHomepage({
        ...defaultGetOffererVenueResponseModel,
        allowedOnAdage: true,
        hasNonDraftOffers: true,
      })

      await user.click(screen.getByRole('tab', { name: /Collectif/ }))
      expect(
        screen.getByRole('tabpanel', { description: /part collective/ })
      ).toBeVisible()
      expect(
        screen.queryByRole('tabpanel', { description: /part individuelle/ })
      ).not.toBeInTheDocument()

      await user.click(screen.getByRole('tab', { name: /Individuel/ }))
      expect(
        screen.queryByRole('tabpanel', { description: /part collective/ })
      ).not.toBeInTheDocument()
      expect(
        screen.getByRole('tabpanel', { description: /part individuelle/ })
      ).toBeVisible()
    })

    describe('initial tab', () => {
      it('when venue has both tabs > should ask for initial tab on load and save the visited tab on tab change', async () => {
        vi.spyOn(utils, 'getInitialTab').mockReturnValue('tab-individual')
        vi.spyOn(utils, 'onNewTabSelected')

        const user = userEvent.setup()
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          allowedOnAdage: true,
          hasNonDraftOffers: true,
        })

        expect(utils.getInitialTab).toHaveBeenCalledOnce()
        expect(
          screen.getByRole('tabpanel', { description: /part individuelle/ })
        ).toBeVisible()

        expect(utils.onNewTabSelected).not.toHaveBeenCalled()

        await user.click(screen.getByRole('tab', { name: /Collectif/ }))
        expect(utils.onNewTabSelected).toHaveBeenCalledWith(
          'tab-collective',
          defaultGetOffererVenueResponseModel.id
        )
      })

      it.each`
        scenario             | hasIndividual | hasCollective | initialTab
        ${'only collective'} | ${false}      | ${true}       | ${'tab-collective'}
        ${'only individual'} | ${true}       | ${false}      | ${'tab-individual'}
        ${'nothing'}         | ${false}      | ${false}      | ${'tab-individual'}
      `(
        'when other scenarii > should handle the $scenario case.',
        ({ hasIndividual, hasCollective, initialTab }) => {
          vi.spyOn(utils, 'getInitialTab').mockReturnValue(initialTab)
          vi.spyOn(utils, 'onNewTabSelected')

          renderNewHomepage({
            ...defaultGetOffererVenueResponseModel,
            allowedOnAdage: hasCollective,
            hasNonDraftOffers: hasIndividual,
          })

          expect(utils.getInitialTab).toHaveBeenCalledExactlyOnceWith(
            defaultGetOffererVenueResponseModel.id,
            hasIndividual,
            hasCollective
          )
          expect(screen.queryByRole('tab')).not.toBeInTheDocument()
          // It's not the Homepage component's role to save the first computed value
          // it's done in tabManagement module
          expect(utils.onNewTabSelected).not.toHaveBeenCalled()
        }
      )
    })
  })

  describe('individual panel', () => {
    /**
     * TODO (mdesquilbet-pass, 2026-02-18): replace text content assertions
     * by mocking components - when all modules are created
     */

    describe('income module', () => {
      it('should be displayed if the venue has non free offers', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          hasNonDraftOffers: true,
          hasNonFreeOffers: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).toHaveTextContent(/Remboursement/)
      })

      it("should not be displayed if the venue doesn't have non free offers", () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          hasNonDraftOffers: true,
          hasNonFreeOffers: false,
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).not.toHaveTextContent(/Remboursement/)
      })
    })

    describe('webinar module', () => {
      beforeEach(() => {
        vi.useFakeTimers()
      })

      afterEach(() => {
        vi.useRealTimers()
      })

      it('should be displayed until the 30th day of venue creation', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 30)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          dateCreated,
          hasNonDraftOffers: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).toHaveTextContent(
          /Participer à nos webinaires sur la part individuelle !/
        )
      })

      it('should not be displayed after the 30th day of venue creation', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 40)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          dateCreated,
          hasNonDraftOffers: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).not.toHaveTextContent(
          /Participer à nos webinaires sur la part indivisuelle !/
        )
      })
    })

    it('should always have the mandatory modules', () => {
      renderNewHomepage({
        ...defaultGetOffererVenueResponseModel,
        hasNonDraftOffers: true,
      })

      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/page partenaire/)

      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Suivez notre actualité/)

      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Comment valoriser vos offres auprès du jeune public/)

      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Evolution de consultation de vos offres/)

      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Activités sur vos offres individuelles/)
    })
  })

  describe('collective panel', () => {
    describe('collective DMS timeline', () => {
      it('should be displayed when venue has a collective DMS application', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: [defaultDMSApplicationForEAC],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(/timeline DMS/)
      })

      it('should not be displayed when venue has not a collective DMS application', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: undefined,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/timeline DMS/)
      })
    })

    describe('individual offers modules', () => {
      it('should be displayed when venue has a refused DMS application', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: [
            {
              ...defaultDMSApplicationForEAC,
              state: DMSApplicationstatus.REFUSE,
            },
          ],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(
          /Proposer vos offres aux jeunes sur l’application mobile pass Culture/
        )
      })

      it('should be displayed when venue has a "sans suite" DMS application', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: [
            {
              ...defaultDMSApplicationForEAC,
              state: DMSApplicationstatus.SANS_SUITE,
            },
          ],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(
          /Proposer vos offres aux jeunes sur l’application mobile pass Culture/
        )
      })

      it('should not be displayed when venue has a pending DMS application', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: [defaultDMSApplicationForEAC],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(
          /Proposer vos offres aux jeunes sur l’application mobile pass Culture/
        )
      })

      it('should not be displayed when venue has no DMS application', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: undefined,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(
          /Proposer vos offres aux jeunes sur l’application mobile pass Culture/
        )
      })
    })

    describe('income module', () => {
      it('should be displayed if the venue has non free offers', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          hasNonFreeOffers: true,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(/Remboursement/)
      })

      it("should not be displayed if the venue doesn't have non free offers", () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          hasNonFreeOffers: false,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/Remboursement/)
      })

      it('should not be displayed when the venue is not allowed on adage', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          hasNonFreeOffers: false,
          allowedOnAdage: false,
          collectiveDmsApplications: [defaultDMSApplicationForEAC],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/Remboursement/)
      })
    })

    describe('mandatory modules', () => {
      it('should always have the mandatory modules when allowed on adage', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(/Activités vos offres vitrines/)

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(/Activités vos offres réservables/)

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(/Votre page sur ADAGE/)

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(/Suivez notre actualité/)
      })

      it('should not  have the mandatory modules when venue is not allowed on adage', () => {
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          allowedOnAdage: false,
          collectiveDmsApplications: [defaultDMSApplicationForEAC],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/Activités vos offres vitrines/)

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/Activités vos offres réservables/)

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/Votre page sur ADAGE/)

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(/Suivez notre actualité/)
      })
    })

    describe('webinar module', () => {
      beforeEach(() => {
        vi.useFakeTimers()
      })

      afterEach(() => {
        vi.useRealTimers()
      })

      it('should be displayed until the 30th day of adage inscription date', () => {
        const adageInscriptionDate = '2026-02-16T12:31:53.443732Z'
        const today = new Date(adageInscriptionDate)
        today.setDate(today.getDate() + 30)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          adageInscriptionDate,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(
          /Participer à nos webinaires sur la part collective !/
        )
      })

      it('should not be displayed after the 30th day of venue creation when venue has no adage inscription date', () => {
        const adageInscriptionDate = '2026-02-16T12:31:53.443732Z'
        const today = new Date(adageInscriptionDate)
        today.setDate(today.getDate() + 40)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          adageInscriptionDate,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(
          /Participer à nos webinaires sur la part collective !/
        )
      })

      it('should be displayed until the 30th day of venue creation when venue has no adage inscription date', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 30)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          dateCreated,
          adageInscriptionDate: null,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).toHaveTextContent(
          /Participer à nos webinaires sur la part collective !/
        )
      })

      it('should not be displayed after the 30th day of venue creation when venue has no adage inscription date', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 40)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          dateCreated,
          adageInscriptionDate: null,
          allowedOnAdage: true,
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(
          /Participer à nos webinaires sur la part collective !/
        )
      })

      it('should not be displayed when venue is not allowed on adage', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 40)
        vi.setSystemTime(today)
        renderNewHomepage({
          ...defaultGetOffererVenueResponseModel,
          dateCreated,
          adageInscriptionDate: null,
          allowedOnAdage: false,
          collectiveDmsApplications: [defaultDMSApplicationForEAC],
        })

        expect(
          screen.getByRole('tabpanel', { description: /collective/ })
        ).not.toHaveTextContent(
          /Participer à nos webinaires sur la part collective !/
        )
      })
    })
  })
})
