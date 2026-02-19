import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererVenueResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import * as utils from './commons/utils'
import { NewHomepage } from './NewHomepage'

const renderNewHomepage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  return renderWithProviders(<NewHomepage />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: defaultGetOffererVenueResponseModel,
      },
    },
    ...options,
  })
}

describe('NewHomepage', () => {
  it('should display the selected venue public name in the title', () => {
    renderNewHomepage()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Votre espace Nom public de la structure'
    )
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
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                allowedOnAdage,
                hasNonDraftOffers,
                collectiveDmsApplications: hasCollectiveDMS
                  ? [defaultDMSApplicationForEAC]
                  : undefined,
              },
            },
          },
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
        storeOverrides: {
          user: {
            selectedVenue: {
              ...defaultGetOffererVenueResponseModel,
              allowedOnAdage: true,
              hasNonDraftOffers: true,
            },
          },
        },
      })

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should display the corresponding panel when click on a given tab', async () => {
      const user = userEvent.setup()
      renderNewHomepage({
        storeOverrides: {
          user: {
            selectedVenue: {
              ...defaultGetOffererVenueResponseModel,
              allowedOnAdage: true,
              hasNonDraftOffers: true,
            },
          },
        },
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
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                allowedOnAdage: true,
                hasNonDraftOffers: true,
              },
            },
          },
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
            storeOverrides: {
              user: {
                selectedVenue: {
                  ...defaultGetOffererVenueResponseModel,
                  allowedOnAdage: hasCollective,
                  hasNonDraftOffers: hasIndividual,
                },
              },
            },
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
    describe('homologation banner', () => {
      it('should not be displayed if the venue is validated', () => {
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                hasNonDraftOffers: true,
                isValidated: true,
              },
            },
          },
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).not.toHaveTextContent(
          /Votre structure est en cours de traitement par les équipes du pass Culture/
        )
      })

      it('should be displayed if the venue is not validated', () => {
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                hasNonDraftOffers: true,
                isValidated: false,
              },
            },
          },
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).toHaveTextContent(
          /Votre structure est en cours de traitement par les équipes du pass Culture/
        )
      })
    })

    describe('budget module', () => {
      it('should be displayed if the venue has non free offers', () => {
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                hasNonDraftOffers: true,
                hasNonFreeOffers: true,
              },
            },
          },
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).toHaveTextContent(/Remboursement/)
      })

      it("should not be displayed if the venue doesn't have non free offers", () => {
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                hasNonDraftOffers: true,
                hasNonFreeOffers: false,
              },
            },
          },
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

      it('should be displayed before the 30st day of venue creation', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 12)
        vi.setSystemTime(today)
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                dateCreated,
                hasNonDraftOffers: true,
              },
            },
          },
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).toHaveTextContent(
          /Participer à nos webinaires sur la part indivisuelle !/
        )
      })

      it('should not be displayed after the 30st day of venue creation', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 40)
        vi.setSystemTime(today)
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                dateCreated,
                hasNonDraftOffers: true,
              },
            },
          },
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).not.toHaveTextContent(
          /Participer à nos webinaires sur la part indivisuelle !/
        )
      })

      it('should be displayed on the 30st day of venue creation', () => {
        const dateCreated = '2026-02-16T12:31:53.443732Z'
        const today = new Date(dateCreated)
        today.setDate(today.getDate() + 30)
        vi.setSystemTime(today)
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                dateCreated,
                hasNonDraftOffers: true,
              },
            },
          },
        })

        expect(
          screen.getByRole('tabpanel', { description: /indiv/ })
        ).toHaveTextContent(
          /Participer à nos webinaires sur la part indivisuelle !/
        )
      })
    })

    it('should always have the mendatory modules', () => {
      renderNewHomepage({
        storeOverrides: {
          user: {
            selectedVenue: {
              ...defaultGetOffererVenueResponseModel,
              hasNonDraftOffers: true,
            },
          },
        },
      })

      // Partner page
      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Votre page sur l’application/)

      // Newsletter
      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Suivez notre actualité/)

      // Edito
      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Comment valoriser vos offres auprès du jeune public/)

      // Stats
      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Evolution de consultation de vos offres/)

      // Offres
      expect(
        screen.getByRole('tabpanel', { description: /indiv/ })
      ).toHaveTextContent(/Activités sur vos offres individuelles/)
    })
  })
})
