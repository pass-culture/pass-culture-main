import '@testing-library/jest-dom'
import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import * as usersSelectors from 'store/selectors/data/usersSelectors'
import { configureTestStore } from 'store/testUtils'

import VenueType from '../../ValueObjects/VenueType'
import VenueEditon from '../VenueEdition'

import { getContactInputs } from './helpers'

jest.mock('../../fields/LocationFields/utils/fetchAddressData', () => ({
  fetchAddressData: jest.fn(),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  getBusinessUnits: jest.fn().mockResolvedValue([]),
  loadProviders: jest.fn().mockResolvedValue([]),
  loadVenueProviders: jest.fn().mockResolvedValue([]),
  getOfferer: jest.fn().mockResolvedValue([]),
  getVenue: jest.fn().mockResolvedValue([]),
}))

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL: 'foo',
}))

const renderVenueEdition = async ({
  props,
  storeOverrides = {},
  url = '/structures/AE/lieux/AQ?modification',
  waitFormRender = true,
}) => {
  const store = configureTestStore(storeOverrides)
  const history = createBrowserHistory()
  history.push(url)

  let rtlRenderReturn
  await act(async () => {
    rtlRenderReturn = await render(
      <Provider store={store}>
        <Router history={history}>
          <VenueEditon {...props} />
        </Router>
      </Provider>
    )
  })

  screen.queryByText('Importation d’offres')
  waitFormRender && (await screen.findByTestId('venue-edition-form'))

  const spinner = screen.queryByTestId('spinner')
  if (spinner) {
    await waitForElementToBeRemoved(() => spinner)
  }

  return {
    history,
    rtlRenderReturn,
  }
}

describe('test page : VenueEdition', () => {
  let push
  let props

  const defaultVenue = {
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
  let venue = { ...defaultVenue }
  let offerer = {
    id: 'BQ',
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
    push = jest.fn()
    props = {
      history: {
        location: {
          pathname: '/fake',
        },
        push: push,
      },
      handleInitialRequest: jest.fn().mockResolvedValue({
        offerer,
        venue,
        venueTypes,
        venueLabels,
      }),
      handleSubmitRequest: jest.fn(),
      handleSubmitRequestSuccess: jest.fn(),
      handleSubmitRequestFail: jest.fn(),
      match: {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      },
      query: {
        changeToReadOnly: jest.fn(),
        context: jest.fn().mockReturnValue({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        }),
      },
    }

    pcapi.getOfferer.mockResolvedValue(offerer)
    pcapi.getVenue.mockResolvedValue(venue)
    pcapi.loadProviders.mockResolvedValue([
      {
        id: 'providerId',
        name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
      },
    ])
    pcapi.getBusinessUnits.mockResolvedValue([{}])
  })

  afterEach(() => {
    venue = { ...defaultVenue }
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
        screen.queryByRole('button', { name: 'Valider' })
      ).toBeInTheDocument()
    })

    it('should not render a Form when venue is virtual', async () => {
      // given
      venue.isVirtual = true

      // when
      await renderVenueEdition({ props, waitFormRender: false })

      // then all form section shoudn't be in the document
      expect(screen.queryByText('Informations lieu')).not.toBeInTheDocument()
      expect(
        screen.queryByText('Coordonnées bancaires du lieu')
      ).not.toBeInTheDocument()
      expect(screen.queryByText('Adresse')).not.toBeInTheDocument()
      expect(screen.queryByText('Accessibilité')).not.toBeInTheDocument()
      expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    })

    it('should render readonly form when venue is virtual and feature flag active', async () => {
      // given
      venue.isVirtual = true
      venue.businessUnit = null
      const storeOverrides = {
        features: {
          list: [
            { isActive: true, nameKey: 'ENFORCE_BANK_INFORMATION_WITH_SIRET' },
          ],
        },
      }

      // when
      await renderVenueEdition({ props, storeOverrides })

      expect(screen.getByText('Informations lieu')).toBeInTheDocument()
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
        screen.queryByText('Label du Ministère de la Culture ou du CNC')
      ).not.toBeInTheDocument()
      expect(screen.queryByText('Description :')).not.toBeInTheDocument()

      expect(screen.queryByText('Adresse')).not.toBeInTheDocument()
      expect(screen.queryByText('Accessibilité')).not.toBeInTheDocument()
      expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    })
  })

  describe('when editing', () => {
    beforeEach(() => {
      props.location = {
        search: '?modifie',
      }
      props.match = {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      }
      props.query.context = () => ({
        readOnly: false,
      })
    })

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
        phoneNumber: '0606060606',
      }
      await clearAndFillContact(contactInfos)

      expect(contactUrl).toHaveValue(contactInfos.website)
      expect(contactPhoneNumber).toHaveValue(contactInfos.phoneNumber)
      expect(contactMail).toHaveValue(contactInfos.email)

      screen.getByText('Valider').click()

      const expectedRequestParams = {
        ...venue,
        contact: {
          email: contactInfos.email,
          phoneNumber: contactInfos.phoneNumber,
          website: contactInfos.website,
        },
      }

      await waitFor(() => {
        expect(props.handleSubmitRequest).toHaveBeenCalledWith(
          expect.objectContaining({ formValues: expectedRequestParams })
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
        screen.queryByRole('button', { name: 'Valider' })
      ).toBeInTheDocument()
    })

    it('should be able to edit address field when venue has no SIRET', async () => {
      // given
      jest
        .spyOn(usersSelectors, 'selectCurrentUser')
        .mockReturnValue({ currentUser: 'fakeUser', publicName: 'fakeName' })

      venue.siret = null

      await renderVenueEdition({ props })
      const addressInput = screen.getByLabelText('Numéro et voie :', {
        exact: false,
      })
      await act(
        async () =>
          await fireEvent.change(addressInput, {
            target: { value: 'Addresse de test' },
          })
      )

      // then
      expect(screen.getByDisplayValue('Addresse de test')).toBeInTheDocument()
    })

    it('should show apply booking checkbox on all existing offers when booking email field is edited', async () => {
      // given
      jest
        .spyOn(usersSelectors, 'selectCurrentUser')
        .mockReturnValue({ currentUser: 'fakeUser', publicName: 'fakeName' })

      const getApplyEmailBookingOnAllOffersLabel = () =>
        screen.queryByText(
          'Utiliser cet email pour me notifier des réservations de toutes les offres déjà postées dans ce lieu.',
          { exact: false }
        )

      // when
      await renderVenueEdition({ props })

      // then
      expect(getApplyEmailBookingOnAllOffersLabel()).not.toBeInTheDocument()

      const informationsNode = screen.getByText('Informations lieu').parentNode
      const emailBookingField = within(informationsNode).getByLabelText(
        'Mail :',
        {
          exact: false,
        }
      )
      // react-final-form interactions need to be wrap into a act()
      await act(
        async () =>
          await fireEvent.change(emailBookingField, {
            target: { value: 'newbookingemail@example.com' },
          })
      )
      expect(getApplyEmailBookingOnAllOffersLabel()).toBeInTheDocument()
    })

    it('should reset url search params and and track venue modification.', async () => {
      // jest
      props.handleSubmitRequest.mockImplementation(({ handleSuccess }) => {
        handleSuccess(jest.fn(), false)()
      })

      // when
      await renderVenueEdition({ props })

      fireEvent.change(await screen.findByLabelText('Téléphone :'), {
        target: { value: '0101010101' },
      })
      fireEvent.click(screen.queryByRole('button', { name: 'Valider' }))

      await waitFor(() => {
        expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null)
      })
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
        await act(async () =>
          fireEvent.change(
            await screen.findByLabelText(
              'Coordonnées bancaires pour vos remboursements :'
            ),
            { target: { value: 21 } }
          )
        )

        fireEvent.click(screen.queryByRole('button', { name: 'Valider' }))

        // Then
        const expectedRequestParams = {
          ...venue,
          businessUnitId: '21',
        }

        expect(props.handleSubmitRequest).toHaveBeenCalledWith(
          expect.objectContaining({ formValues: expectedRequestParams })
        )
      })

      it('should display confirmation dialog when edit business unit main venue', async () => {
        // Given
        venue.isBusinessUnitMainVenue = true

        await renderVenueEdition({ props, storeOverrides })

        // When
        await act(async () =>
          fireEvent.change(
            await screen.findByLabelText(
              'Coordonnées bancaires pour vos remboursements :'
            ),
            { target: { value: 21 } }
          )
        )

        fireEvent.click(screen.queryByRole('button', { name: 'Valider' }))

        // Then
        expect(props.handleSubmitRequest).not.toHaveBeenCalled()

        expect(
          screen.getByText(
            'Vous allez modifier les coordonnées bancaires associées à ce lieu'
          )
        ).toBeInTheDocument()
        fireEvent.click(screen.getByRole('button', { name: 'Continuer' }))
        expect(props.handleSubmitRequest).toHaveBeenCalledTimes(1)
      })

      it('should not submit data when cancel edition of business unit main venue', async () => {
        // Given
        venue.isBusinessUnitMainVenue = true

        await renderVenueEdition({ props, storeOverrides })

        // When
        await act(async () =>
          fireEvent.change(
            await screen.findByLabelText(
              'Coordonnées bancaires pour vos remboursements :'
            ),
            { target: { value: 21 } }
          )
        )

        fireEvent.click(screen.queryByRole('button', { name: 'Valider' }))
        expect(
          screen.getByText(
            'Vous allez modifier les coordonnées bancaires associées à ce lieu'
          )
        ).toBeInTheDocument()

        fireEvent.click(screen.getByRole('button', { name: 'Annuler' }))

        // Then
        expect(props.handleSubmitRequest).not.toHaveBeenCalled()
      })

      it('should not display confirmation dialog when edit business unit not main venue', async () => {
        // Given
        venue.isBusinessUnitMainVenue = false
        await renderVenueEdition({ props, storeOverrides })

        const bankSelect = await screen.findByLabelText(
          'Coordonnées bancaires pour vos remboursements :'
        )

        // When
        fireEvent.change(bankSelect, { target: { value: 21 } })
        fireEvent.click(screen.queryByRole('button', { name: 'Valider' }))

        // Then
        await waitFor(() => {
          expect(props.handleSubmitRequest).toHaveBeenCalledTimes(1)
        })
      })
    })

    describe('image uploader', () => {
      it('hides when venue is not permanent', async () => {
        venue.isPermanent = false

        await renderVenueEdition({ props })

        expect(
          screen.queryByTestId('image-venue-uploader-section')
        ).not.toBeInTheDocument()
      })

      it('displays when feature flag is enabled and venue is permanent', async () => {
        venue.isPermanent = true

        await renderVenueEdition({ props })

        expect(
          screen.queryByTestId('image-venue-uploader-section')
        ).toBeInTheDocument()
      })
    })
  })

  describe('when reading', () => {
    beforeEach(() => {
      props.query.context = () => ({
        isCreatedEntity: false,
        isModifiedEntity: false,
        readOnly: true,
      })
    })

    it('should display disabled contact fields', async () => {
      await renderVenueEdition({ props })
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
      await renderVenueEdition({ props })

      // then
      // todo: check submit button state
      expect(
        screen.queryByRole('link', { name: 'Terminer' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Valider' })
      ).not.toBeInTheDocument()
    })

    describe('create new offer link', () => {
      it('should redirect to offer creation page', async () => {
        // given
        jest
          .spyOn(usersSelectors, 'selectCurrentUser')
          .mockReturnValue({ currentUser: 'fakeUser' })

        venue.id = 'CM'

        const { history } = await renderVenueEdition({
          props,
          url: '/structures/APEQ/lieux/CM',
        })
        const createOfferLink = screen.getByText('Créer une offre')

        // when
        fireEvent.click(createOfferLink)

        // then
        // todo: check location url or add a text in a fake offer creation route and test that it's displayed
        expect(`${history.location.pathname}${history.location.search}`).toBe(
          '/offre/creation?lieu=CM&structure=APEQ'
        )
      })
    })
  })
})
