import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '../../commons/__mocks__/constants'
import {
  IndividualOfferLocationScreen,
  type IndividualOfferLocationScreenProps,
} from './IndividualOfferLocationScreen'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
  },
}))

const renderIndividualOfferLocationScreen: RenderComponentFunction<
  IndividualOfferLocationScreenProps,
  IndividualOfferContextValues
> = (params) => {
  const offer = getIndividualOfferFactory()
  const venues = [
    {
      ...makeVenueListItem({
        id: 1,
        publicName: 'Lieu Nom Public Pour Test',
      }),
      location: {
        banId: '75101_9575_00003',
        city: 'Paris',
        id: 945,
        inseeCode: '75056',
        isVenueLocation: false,
        isManualEdition: false,
        label: 'MINISTERE DE LA CULTURE',
        latitude: 48.87171,
        longitude: 2.30829,
        postalCode: '75001',
        street: '3 Rue de Valois',
      },
    },
  ]
  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: null,
    setIsEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    offer,
    offerId: offer.id,
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }
  const props: IndividualOfferLocationScreenProps = {
    offer,
    venues,
    ...params.props,
  }

  // Ensure components reading offer from context (e.g., LocationForm) get the same offer as props by default
  contextValues.offer = props.offer ?? contextValues.offer

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferLocationScreen {...props} />
    </IndividualOfferContext.Provider>,
    options
  )
}

const LABELS = {
  titles: {
    main: 'Où profiter de l’offre ?',
  },
  buttons: {
    saveAndContinue: 'Enregistrer et continuer',
    saveAndGoBack: 'Enregistrer les modifications',
    cantFindAddress: /Vous ne trouvez pas votre adresse \?/,
  },
  fields: {
    address: `Il s’agit de l’adresse à laquelle les jeunes devront se présenter. *`,
    url: /URL d’accès à l’offre/,
    addressLocationLabel: 'Intitulé de la localisation',
    street: 'Adresse postale',
    postalCode: 'Code postal',
    city: 'Ville',
    coords: 'Coordonnées GPS',
  },
  options: {
    venueAddress: 'Lieu Nom Public Pour Test – 3 Rue de Valois 75001 Paris',
    otherAddress: 'À une autre adresse',
  },
}

describe('<IndividualOfferLocationScreen />', () => {
  describe('when offer subcategory is OFFLINE', () => {
    const offlineOffer = getIndividualOfferFactory({
      id: 3,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
      venue: getOfferVenueFactory({ id: 1 }),
    })

    describe('when mode is CREATION', () => {
      beforeEach(() => {
        vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
          useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
        }))
      })

      it('should render and pass accessibility checks', async () => {
        const props = { offer: offlineOffer }

        const { container } = renderIndividualOfferLocationScreen({ props })

        expect(
          await screen.findByRole('heading', { name: LABELS.titles.main })
        ).toBeInTheDocument()

        expect(
          //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
          await axe(container, {
            rules: { 'color-contrast': { enabled: false } },
          })
        ).toHaveNoViolations()
      })

      it('should submit the venue address payload when a venue address is selected', async () => {
        vi.spyOn(api, 'patchOffer').mockResolvedValue(offlineOffer)

        const props = { offer: offlineOffer }

        renderIndividualOfferLocationScreen({ props })

        await userEvent.click(
          screen.getByRole('radio', {
            name: 'Lieu Nom Public Pour Test – 3 Rue de Valois 75001 Paris',
          })
        )

        await userEvent.click(
          screen.getByRole('button', { name: /Enregistrer/ })
        )

        expect(api.patchOffer).toHaveBeenCalledOnce()
        expect(api.patchOffer).toHaveBeenCalledWith(
          3,
          expect.objectContaining({
            location: expect.objectContaining({
              city: 'Paris',
              isManualEdition: false,
              isVenueLocation: true,
              label: 'MINISTERE DE LA CULTURE',
              latitude: '48.87171',
              longitude: '2.30829',
              postalCode: '75001',
              street: '3 Rue de Valois',
              banId: '75101_9575_00003',
              inseeCode: '75056',
            }),
            shouldSendMail: false,
          })
        )
      })
    })

    describe('when mode is EDITION', () => {
      beforeEach(() => {
        vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
          useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.EDITION),
        }))
      })

      it('should render and pass accessibility checks', async () => {
        const props = { offer: offlineOffer }

        const { container } = renderIndividualOfferLocationScreen({ props })

        expect(
          await screen.findByRole('heading', { name: LABELS.titles.main })
        ).toBeInTheDocument()

        expect(
          //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
          await axe(container, {
            rules: { 'color-contrast': { enabled: false } },
          })
        ).toHaveNoViolations()
      })

      describe('should open the update warning dialog before saving when address changed and offer has pending bookings', () => {
        const offlineOfferWithPendingBookings = {
          ...offlineOffer,
          location: {
            banId: '12',
            inseeCode: '13',
            postalCode: '12345',
            street: 'Rue',
            city: 'Test-sur-Seine',
            latitude: 1.23,
            longitude: 4.56,
            departmentCode: '12',
            label: 'Etiquette de lieu',
            id: 14,
            isVenueLocation: false,
            isManualEdition: false,
          },
          hasPendingBookings: true,
        }

        beforeEach(async () => {
          vi.spyOn(api, 'patchOffer').mockResolvedValue(
            offlineOfferWithPendingBookings
          )

          renderIndividualOfferLocationScreen({
            props: { offer: offlineOfferWithPendingBookings },
          })

          await userEvent.click(
            screen.getByRole('radio', { name: LABELS.options.otherAddress })
          )
          await userEvent.type(
            screen.getByRole('textbox', {
              name: LABELS.fields.addressLocationLabel,
            }),
            'Etiquette de lieu modifié'
          )
          await userEvent.click(
            screen.getByRole('button', { name: LABELS.buttons.saveAndGoBack })
          )
        })

        it('and behave as expected', async () => {
          expect(
            await screen.findByText(
              'Les changements vont s’appliquer à l’ensemble des réservations en cours associées'
            )
          ).toBeInTheDocument()
          expect(api.patchOffer).not.toHaveBeenCalled()
        })

        // `shouldSendMail` checkbox is checked by default
        it('and send shouldSendMail=true to API when checked', async () => {
          await userEvent.click(
            screen.getByRole('button', { name: 'Je confirme le changement' })
          )

          await waitFor(() => {
            expect(api.patchOffer).toHaveBeenCalledWith(
              offlineOfferWithPendingBookings.id,
              expect.objectContaining({ shouldSendMail: true })
            )
          })
        })

        // `shouldSendMail` checkbox is checked by default
        it('and send shouldSendMail=false to API when checked', async () => {
          // = uncheck since `shouldSendMail` checkbox is checked by default
          await userEvent.click(
            await screen.findByRole('checkbox', {
              name: 'Prévenir les jeunes par e-mail',
            })
          )

          await userEvent.click(
            screen.getByRole('button', { name: 'Je confirme le changement' })
          )

          await waitFor(() => {
            expect(api.patchOffer).toHaveBeenCalledWith(
              offlineOfferWithPendingBookings.id,
              expect.objectContaining({ shouldSendMail: false })
            )
          })
        })

        it('and close the dialog without saving when canceled', async () => {
          expect(
            await screen.findByText(
              'Les changements vont s’appliquer à l’ensemble des réservations en cours associées'
            )
          ).toBeInTheDocument()

          await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

          expect(
            screen.queryByText(
              'Les changements vont s’appliquer à l’ensemble des réservations en cours associées'
            )
          ).not.toBeInTheDocument()
          expect(api.patchOffer).not.toHaveBeenCalled()
        })
      })
    })
  })

  describe('when offer is digital', () => {
    const onlineOffer = getIndividualOfferFactory({
      id: 3,
      isDigital: true,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_ONLINE.id,
      venue: getOfferVenueFactory({ id: 1 }),
    })

    describe('when mode is CREATION', () => {
      beforeEach(() => {
        vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
          useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
        }))
      })

      it('should render and pass accessibility checks', async () => {
        const props = { offer: onlineOffer }

        const { container } = renderIndividualOfferLocationScreen({ props })

        expect(
          await screen.findByRole('heading', { name: LABELS.titles.main })
        ).toBeInTheDocument()

        expect(
          //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
          await axe(container, {
            rules: { 'color-contrast': { enabled: false } },
          })
        ).toHaveNoViolations()
      })

      it('should render without error even when url is null', async () => {
        const props = { offer: { ...onlineOffer, url: null } }

        renderIndividualOfferLocationScreen({ props })

        expect(
          await screen.findByRole('heading', { name: LABELS.titles.main })
        ).toBeInTheDocument()

        expect(
          screen.getByRole('textbox', { name: LABELS.fields.url })
        ).toBeInTheDocument()
      })
    })

    describe('when mode is EDITION', () => {
      beforeEach(() => {
        vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
          useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.EDITION),
        }))
      })

      it('should render and pass accessibility checks', async () => {
        const props = { offer: onlineOffer }

        const { container } = renderIndividualOfferLocationScreen({ props })

        expect(
          await screen.findByRole('heading', { name: LABELS.titles.main })
        ).toBeInTheDocument()

        expect(
          //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
          await axe(container, {
            rules: { 'color-contrast': { enabled: false } },
          })
        ).toHaveNoViolations()
      })

      it('should show only the URL field', async () => {
        const props = { offer: onlineOffer }

        renderIndividualOfferLocationScreen({ props })

        expect(
          await screen.findByRole('heading', { name: LABELS.titles.main })
        ).toBeInTheDocument()

        expect(
          screen.getByRole('textbox', { name: LABELS.fields.url })
        ).toBeInTheDocument()

        expect(
          screen.queryByRole('group', {
            name: LABELS.fields.address,
          })
        ).not.toBeInTheDocument()
      })

      it('should disable the URL field if another offer with the same EAN exists', async () => {
        const contextValues = { hasPublishedOfferWithSameEan: true }
        const props = { offer: onlineOffer }

        renderIndividualOfferLocationScreen({ contextValues, props })

        expect(
          await screen.findByRole('textbox', { name: LABELS.fields.url })
        ).toBeDisabled()
      })
    })
  })
})
