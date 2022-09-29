import '@testing-library/jest-dom'

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import * as usersSelectors from 'store/user/selectors'

import VenueType from '../../ValueObjects/VenueType'
import VenueEditon from '../VenueEdition'

import { getContactInputs } from './helpers'

jest.mock('../../fields/LocationFields/utils/fetchAddressData', () => ({
  fetchAddressData: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'BQ',
    venueId: 'AQ',
  }),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  getBusinessUnits: jest.fn().mockResolvedValue([]),
  loadProviders: jest.fn().mockResolvedValue([]),
  loadVenueProviders: jest.fn().mockResolvedValue([]),
  getVenueLabels: jest.fn().mockResolvedValue([]),
  editVenue: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    canOffererCreateEducationalOffer: jest.fn(),
    getOfferer: jest.fn().mockResolvedValue([]),
    getVenue: jest.fn().mockResolvedValue({}),
    getAvailableReimbursementPoints: jest.fn(),
    getVenueTypes: jest.fn().mockResolvedValue([]),
  },
}))

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL: 'foo',
}))

const renderVenueEdition = async ({
  props,
  storeOverrides = {},
  initialEntries = '/structures/AM/lieux/AE?modification',
}) => {
  const store = configureTestStore(storeOverrides)

  let rtlRenderReturn = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[initialEntries]}>
        <VenueEditon {...props} />
      </MemoryRouter>
    </Provider>
  )

  await waitFor(() => {
    expect(screen.queryByText('Lieu')).toBeInTheDocument()
  })

  return {
    rtlRenderReturn,
  }
}

describe('test page : VenueEdition', () => {
  let props = {}

  const venue = {
    noDisabilityCompliant: false,
    isAccessibilityAppliedOnAllOffers: true,
    audioDisabilityCompliant: true,
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    visualDisabilityCompliant: true,
    address: '1 boulevard Poissonnière',
    bookingEmail: 'fake@example.com',
    city: 'Paris',
    dateCreated: '2021-09-13T14:59:21.661969Z',
    dateModifiedAtLastProvider: '2021-09-13T14:59:21.661955Z',
    departementCode: '75',
    id: 'AQ',
    isBusinessUnitMainVenue: false,
    isValidated: true,
    isVirtual: false,
    isPermanent: true,
    latitude: 48.91683,
    longitude: 2.43884,
    managingOffererId: 'AM',
    nOffers: 7,
    name: 'Maison de la Brique',
    postalCode: '75000',
    publicName: 'Maison de la Brique',
    siret: '22222222311111',
    venueTypeCode: 'DE',
    businessUnit: { id: 20 },
    businessUnitId: 20,
    contact: {
      email: 'contact@venue.com',
      website: 'https://my@website.com',
      phoneNumber: '+33102030405',
    },
  }
  let offerer = {
    id: 'AM',
    name: 'Maison du chocolat',
  }
  const venueTypes = [
    new VenueType({
      id: 'VISUAL_ARTS',
      label: 'Arts visuels, arts plastiques et galeries',
    }),
  ]
  const venueLabels = []

  beforeEach(() => {
    api.getOfferer.mockResolvedValue(offerer)
    api.getVenue.mockResolvedValue(venue)
    api.getVenueTypes.mockResolvedValue(venueTypes)
    pcapi.getVenueLabels.mockResolvedValue(venueLabels)

    api.getOfferer.mockResolvedValue(offerer)
    api.getVenue.mockResolvedValue(venue)
    pcapi.loadProviders.mockResolvedValue([
      {
        id: 'providerId',
        name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
      },
    ])
    pcapi.getBusinessUnits.mockResolvedValue([{}])
    api.canOffererCreateEducationalOffer.mockResolvedValue()
  })

  describe('render', () => {
    it('should render component with default state', async () => {
      // when
      await renderVenueEdition({ props })

      // then
      expect(
        screen.queryByRole('link', { name: 'Terminer' })
      ).not.toBeInTheDocument()
      expect(
        await screen.findByRole('button', { name: 'Valider' })
      ).toBeInTheDocument()
    })

    it('should not render a Form when venue is virtual', async () => {
      // given
      const virtualVenue = {
        noDisabilityCompliant: false,
        isAccessibilityAppliedOnAllOffers: true,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        bookingEmail: 'fake@example.com',
        dateCreated: '2021-09-13T14:59:21.661969Z',
        dateModifiedAtLastProvider: '2021-09-13T14:59:21.661955Z',
        id: 'AQ',
        isBusinessUnitMainVenue: false,
        isValidated: true,
        isVirtual: true,
        managingOffererId: 'AM',
        nOffers: 7,
        name: 'Maison de la Brique (Offre Numérique)',
        siret: '22222222311111',
        venueTypeCode: 'DE',
        businessUnit: { id: 20 },
        businessUnitId: 20,
        contact: {
          email: 'contact@venue.com',
          website: 'https://my@website.com',
          phoneNumber: '+33102030405',
        },
      }
      api.getVenue.mockResolvedValue({ ...virtualVenue })

      // when
      await renderVenueEdition({ props, waitFormRender: false })

      // then some form section shoudn't be in the document
      expect(screen.queryByText('Adresse')).not.toBeInTheDocument()
      expect(screen.queryByText('Accessibilité')).not.toBeInTheDocument()
      expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    })

    it('should render readonly form when venue is virtual and feature flag active', async () => {
      // given
      api.getVenue.mockResolvedValue({
        ...venue,
        isVirtual: true,
        businessUnit: true,
      })
      const storeOverrides = {
        features: {
          list: [
            { isActive: true, nameKey: 'ENFORCE_BANK_INFORMATION_WITH_SIRET' },
          ],
        },
      }

      // when
      await renderVenueEdition({ props, storeOverrides })

      expect(await screen.findByText('Informations lieu')).toBeInTheDocument()
      await expect(
        screen.findByText('Coordonnées bancaires du lieu')
      ).resolves.toBeInTheDocument()

      const informationsNode = screen.getByText('Informations lieu').parentNode
      expect(screen.getByLabelText('Nom du lieu :')).toBeDisabled()
      expect(within(informationsNode).getByLabelText('Mail :')).toBeDisabled()
      expect(screen.getByText('Offre numérique')).toBeInTheDocument()
      expect(screen.queryByText('SIRET :')).not.toBeInTheDocument()
      expect(
        screen.queryByText("Nom d'usage du lieu :")
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Commentaire (si pas de SIRET) :')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Label du Ministère de la Culture ou du CNC :')
      ).not.toBeInTheDocument()
      expect(screen.queryByText('Description :')).not.toBeInTheDocument()

      expect(screen.queryByText('Adresse')).not.toBeInTheDocument()
      expect(screen.queryByText('Accessibilité')).not.toBeInTheDocument()
      expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    })
  })

  describe('when editing', () => {
    it('should display contact fields', async () => {
      await renderVenueEdition({ props })
      const { contactPhoneNumber, contactMail, contactUrl } =
        await getContactInputs()

      expect(contactPhoneNumber).toBeInTheDocument()
      expect(contactMail).toBeInTheDocument()
      expect(contactUrl).toBeInTheDocument()

      expect(contactPhoneNumber).toBeEnabled()
      expect(contactMail).toBeEnabled()
      expect(contactUrl).toBeEnabled()

      expect(contactUrl).toHaveValue(venue.contact.website)
      expect(contactPhoneNumber).toHaveValue(venue.contact.phoneNumber)
      expect(contactMail).toHaveValue(venue.contact.email)
    })

    it('should be able to edit contact fields', async () => {
      await renderVenueEdition({ props })
      const {
        contactPhoneNumber,
        contactMail,
        contactUrl,
        clearAndFillContact,
      } = await getContactInputs()
      const contactInfos = {
        email: 'test@test.com',
        website: 'https://some-url-test.com',
        phoneNumber: '+33606060606',
      }
      await clearAndFillContact(contactInfos)

      expect(contactUrl).toHaveValue(contactInfos.website)
      expect(contactPhoneNumber).toHaveValue(contactInfos.phoneNumber)
      expect(contactMail).toHaveValue(contactInfos.email)

      screen.getByText('Valider').click()

      const expectedRequestParams = {
        contact: {
          email: contactInfos.email,
          phoneNumber: contactInfos.phoneNumber,
          website: contactInfos.website,
        },
      }

      await waitFor(() => {
        expect(pcapi.editVenue).toHaveBeenCalledWith(
          'AQ',
          expect.objectContaining(expectedRequestParams)
        )
      })
    })

    it('should render component with correct state values', async () => {
      // when
      await renderVenueEdition({ props })

      // then
      expect(
        screen.queryByRole('link', { name: 'Terminer' })
      ).not.toBeInTheDocument()
      expect(
        await screen.findByRole('button', { name: 'Valider' })
      ).toBeInTheDocument()
    })

    it('should be able to edit address field when venue has no SIRET', async () => {
      // given
      jest
        .spyOn(usersSelectors, 'selectCurrentUser')
        .mockReturnValue({ currentUser: 'fakeUser', publicName: 'fakeName' })

      api.getVenue.mockResolvedValue({
        ...venue,
        siret: null,
      })

      await renderVenueEdition({ props })
      const addressInput = await screen.findByLabelText(/Numéro et voie :/)

      await userEvent.clear(addressInput)
      await userEvent.type(addressInput, 'Addresse de test')

      // then
      expect(
        await screen.findByDisplayValue('Addresse de test')
      ).toBeInTheDocument()
    })

    it('should show apply booking checkbox on all existing offers when booking email field is edited', async () => {
      // given
      jest
        .spyOn(usersSelectors, 'selectCurrentUser')
        .mockReturnValue({ currentUser: 'fakeUser', publicName: 'fakeName' })

      // when
      await renderVenueEdition({ props })

      // then
      expect(
        screen.queryByText(
          /Utiliser cet email pour me notifier des réservations de toutes les offres déjà postées dans ce lieu./
        )
      ).not.toBeInTheDocument()

      const informationsNode = await (
        await screen.findByText('Informations lieu')
      ).parentNode

      const emailBookingField = await within(informationsNode).findByLabelText(
        'Mail :',
        {
          exact: false,
        }
      )

      await userEvent.type(emailBookingField, 'newbookingemail@example.com')

      expect(
        await screen.findByText(
          /Utiliser cet email pour me notifier des réservations de toutes les offres déjà postées dans ce lieu./
        )
      ).toBeInTheDocument()
    })

    it('should reset url search params and and track venue modification.', async () => {
      // jest
      pcapi.editVenue.mockResolvedValue(true)

      // when
      await renderVenueEdition({ props })

      const telField = await screen.findByLabelText('Téléphone :')
      await userEvent.clear(telField)
      await userEvent.type(telField, '0101010101')
      await userEvent.click(screen.queryByRole('button', { name: 'Valider' }))

      await waitFor(() => {
        expect(window.location.href).not.toContain('modification')
      })
    })

    it('should be able to edit when venue does not have reimbursement point', async () => {
      const storeOverrides = {
        features: {
          list: [
            {
              nameKey: 'ENABLE_NEW_BANK_INFORMATIONS_CREATION',
              isActive: true,
            },
          ],
        },
      }
      jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([
        {
          iban: 'FR0000000000000001',
          name: 'Business unit #1',
          venueName: 'Reimbursement point #1',
        },
      ])

      await renderVenueEdition({ props, storeOverrides })

      const publicNameInput = await screen.findByLabelText(
        'Nom d’usage du lieu :'
      )
      await userEvent.clear(publicNameInput)
      await userEvent.type(publicNameInput, 'Mon lieu')

      await userEvent.click(screen.queryByRole('button', { name: 'Valider' }))

      expect(pcapi.editVenue).toHaveBeenCalledWith(
        'AQ',
        expect.objectContaining({
          reimbursementPointId: null,
          publicName: 'Mon lieu',
        })
      )
    })

    describe('bank information', () => {
      const storeOverrides = {
        features: {
          list: [
            {
              nameKey: 'ENFORCE_BANK_INFORMATION_WITH_SIRET',
              isActive: true,
            },
          ],
        },
      }
      beforeEach(() => {
        pcapi.getBusinessUnits.mockResolvedValue([
          {
            id: 20,
            iban: 'FR0000000000000002',
            name: 'Business unit #1',
            siret: '22222222311111',
          },
          {
            id: 21,
            iban: 'FR0000000000000003',
            name: 'Business unit #2',
            siret: '22222222311222',
          },
        ])
      })

      it('should be able to edit bank information', async () => {
        // Given
        await renderVenueEdition({ props, storeOverrides })

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(
            'Coordonnées bancaires pour vos remboursements :'
          ),
          '21'
        )

        await userEvent.click(screen.queryByRole('button', { name: 'Valider' }))

        // Then

        await waitFor(() =>
          expect(pcapi.editVenue).toHaveBeenCalledWith(
            'AQ',
            expect.objectContaining({
              address: venue.address,
              businessUnitId: '21',
            })
          )
        )
      })

      it('should display confirmation dialog when edit business unit main venue', async () => {
        // Given
        api.getVenue.mockResolvedValue({
          ...venue,
          isBusinessUnitMainVenue: true,
        })

        await renderVenueEdition({ props, storeOverrides })

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(
            'Coordonnées bancaires pour vos remboursements :'
          ),
          '21'
        )

        await userEvent.click(screen.queryByRole('button', { name: 'Valider' }))

        // Then
        expect(pcapi.editVenue).not.toHaveBeenCalled()

        expect(
          await screen.findByText(
            'Vous allez modifier les coordonnées bancaires associées à ce lieu'
          )
        ).toBeInTheDocument()
        await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
        expect(pcapi.editVenue).toHaveBeenCalledTimes(1)
      })

      it('should not submit data when cancel edition of business unit main venue', async () => {
        // Given
        pcapi.getBusinessUnits.mockResolvedValue([
          {
            id: 20,
            iban: 'FR0000000000000002',
            name: 'Business unit #1',
            siret: '22222222311111',
          },
          {
            id: 21,
            iban: 'FR0000000000000003',
            name: 'Business unit #2',
            siret: '22222222311222',
          },
        ])
        api.getVenue.mockResolvedValue({
          ...venue,
          isBusinessUnitMainVenue: true,
        })
        await renderVenueEdition({ props, storeOverrides })

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(
            'Coordonnées bancaires pour vos remboursements :'
          ),
          '21'
        )

        await userEvent.click(screen.getByRole('button', { name: 'Valider' }))
        expect(
          await screen.findByText(
            'Vous allez modifier les coordonnées bancaires associées à ce lieu'
          )
        ).toBeInTheDocument()

        await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

        // Then
        expect(pcapi.editVenue).not.toHaveBeenCalled()
      })

      it('should not display confirmation dialog when edit business unit not main venue', async () => {
        // Given
        await renderVenueEdition({ props, storeOverrides })

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(
            'Coordonnées bancaires pour vos remboursements :'
          ),
          '21'
        )
        await userEvent.click(screen.queryByRole('button', { name: 'Valider' }))

        // Then
        await waitFor(() => {
          expect(pcapi.editVenue).toHaveBeenCalledTimes(1)
        })
      })
    })

    describe('image uploader', () => {
      it('hides when venue is not permanent', async () => {
        api.getVenue.mockResolvedValue({
          ...venue,
          isPermanent: false,
        })
        await renderVenueEdition({ props })

        expect(
          screen.queryByTestId('image-venue-uploader-section')
        ).not.toBeInTheDocument()
      })

      it('displays when feature flag is enabled and venue is permanent', async () => {
        api.getVenue.mockResolvedValue({
          ...venue,
          isPermanent: true,
        })
        await renderVenueEdition({ props })

        expect(
          await screen.findByTestId('image-venue-uploader-section')
        ).toBeInTheDocument()
      })
    })

    describe('EAC Information', () => {
      it('should display EAC Information block when offerer can create collective offer', async () => {
        await renderVenueEdition({ props })

        const eacSection = await screen.findByText(
          'Mes informations pour les enseignants',
          {
            selector: 'h2',
          }
        )
        expect(eacSection).toBeInTheDocument()
      })

      it('should not display EAC Information block when offerer cannot create collective offer', async () => {
        api.canOffererCreateEducationalOffer.mockRejectedValueOnce()
        await renderVenueEdition({ props })

        const eacSection = screen.queryByText(
          'Mes informations pour les enseignants',
          {
            selector: 'h2',
          }
        )
        expect(eacSection).not.toBeInTheDocument()
      })
    })
  })

  describe('when reading', () => {
    it('should display disabled contact fields', async () => {
      await renderVenueEdition({ initialEntries: '/structures/AE/lieux/AE' })
      const { contactPhoneNumber, contactMail, contactUrl } =
        await getContactInputs()

      expect(contactPhoneNumber).toBeInTheDocument()
      expect(contactMail).toBeInTheDocument()
      expect(contactUrl).toBeInTheDocument()

      expect(contactPhoneNumber).toBeDisabled()
      expect(contactMail).toBeDisabled()
      expect(contactUrl).toBeDisabled()

      expect(contactUrl).toHaveValue(venue.contact.website)
      expect(contactPhoneNumber).toHaveValue(venue.contact.phoneNumber)
      expect(contactMail).toHaveValue(venue.contact.email)
    })

    it('should render component with correct state values', async () => {
      // when
      await renderVenueEdition({ initialEntries: '/structures/AE/lieux/AE' })

      // then
      // todo: check submit button state
      expect(
        await screen.findByRole('link', { name: 'Terminer' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Valider' })
      ).not.toBeInTheDocument()
    })

    describe('create new offer link', () => {
      it('should redirect to offer creation page', async () => {
        api.getVenue.mockResolvedValue({ ...venue, id: 'CM' })
        // given
        await renderVenueEdition({ initialEntries: '/structures/AE/lieux/AE' })
        // when
        const createOfferLink = await screen.findByRole('link', {
          name: /Créer une offre/,
        })
        // then
        expect(createOfferLink).toHaveAttribute(
          'href',
          '/offre/creation?lieu=CM&structure=BQ'
        )
      })
    })
  })
})
