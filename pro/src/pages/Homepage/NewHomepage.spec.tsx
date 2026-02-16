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

        // It's not the Homepage component's role to save the first computed value
        // it's done in getInitialTab function
        expect(utils.onNewTabSelected).not.toHaveBeenCalled()

        await user.click(screen.getByRole('tab', { name: /Collectif/ }))
        expect(utils.onNewTabSelected).toHaveBeenCalledWith(
          'tab-collective',
          defaultGetOffererVenueResponseModel.id
        )
      })

      it.each`
        scenario             | venue    | hasIndividual | hasCollective | initialTab
        ${'only collective'} | ${true}  | ${false}      | ${true}       | ${'tab-collective'}
        ${'only individual'} | ${true}  | ${true}       | ${false}      | ${'tab-individual'}
        ${'nothing'}         | ${true}  | ${false}      | ${false}      | ${'tab-individual'}
        ${'no venue '}       | ${false} | ${false}      | ${false}      | ${'tab-individual'}
      `(
        'when other scenarii > should handle the $scenario case.',
        ({ venue, hasIndividual, hasCollective, initialTab }) => {
          vi.spyOn(utils, 'getInitialTab').mockReturnValue(initialTab)
          vi.spyOn(utils, 'onNewTabSelected')

          renderNewHomepage({
            storeOverrides: {
              user: {
                selectedVenue: venue
                  ? {
                      ...defaultGetOffererVenueResponseModel,
                      allowedOnAdage: hasCollective,
                      hasNonDraftOffers: hasIndividual,
                    }
                  : null,
              },
            },
          })

          expect(utils.getInitialTab).toHaveBeenCalledExactlyOnceWith(
            venue ? defaultGetOffererVenueResponseModel.id : null,
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
})
