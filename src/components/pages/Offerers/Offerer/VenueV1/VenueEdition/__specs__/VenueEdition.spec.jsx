import '@testing-library/jest-dom'
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from "history"
import React from "react"
import { Provider } from "react-redux"
import { Router } from "react-router-dom"

import { configureTestStore } from "../../../../../../../store/testUtils"
import VenueEditon from "../VenueEdition"

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  loadProviders: jest.fn().mockResolvedValue([]),
  loadVenueProviders: jest.fn().mockResolvedValue([]),
}))

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL: 'foo'
}))

const renderVenueEdition = ({ props }) => {
  const store = configureTestStore()
  const history = createBrowserHistory()
  history.push(`/structures/AE/lieux/TR?modification`)

  const utils = render(
    <Provider store={store}>
      <Router history={history}>
        <VenueEditon {...props} />
      </Router>
    </Provider>
  )

  const getContactInputs = async () => {
    const contactPhoneNumber = await screen.findByLabelText("Téléphone :")
    const contactMail = await screen.findByLabelText("Mail :")
    const contactUrl = await screen.findByLabelText("URL de votre site web :")

    const clearAndFillContact = ({ phone, mail, website })=>{
      userEvent.clear(contactPhoneNumber)
      userEvent.clear(contactMail)
      userEvent.clear(contactUrl)

      userEvent.paste(contactPhoneNumber, phone)
      userEvent.paste(contactMail, mail)
      userEvent.paste(contactUrl, website)
    }

    return {
      contactPhoneNumber,
      contactMail,
      contactUrl,
      clearAndFillContact
    }
  }

  return  {
    ...utils,
    getContactInputs
  }
}

describe('contact form enable in venue creation form', () => {

  let push
  let props

  beforeEach(() => {
    push = jest.fn()
    props = {
      venue: {
        noDisabilityCompliant: false,
        isAccessibilityAppliedOnAllOffers: true,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        address: "1 boulevard Poissonnière",
        bookingEmail: "fake@example.com",
        city: "Paris",
        dateCreated: "2021-09-13T14:59:21.661969Z",
        dateModifiedAtLastProvider: "2021-09-13T14:59:21.661955Z",
        departementCode: "75",
        id: "AQ",
        isValidated: true,
        isVirtual: false,
        latitude: 48.91683,
        longitude: 2.43884,
        managingOffererId: "AM",
        nOffers: 7,
        name: "Maison de la Brique",
        postalCode: "75000",
        publicName: "Maison de la Brique",
        siret: "22222222311111",
        venueTypeId: "DE",
      },
      history: {
        location: {
          pathname: '/fake',
        },
        push: push,
      },
      withdrawalDetailActive: true,
      handleInitialRequest: jest.fn(),
      handleSubmitRequest: jest.fn(),
      handleSubmitRequestSuccess: jest.fn(),
      handleSubmitRequestFail: jest.fn(),
      match: {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      },
      offerer: {
        id: 'BQ',
        name: 'Maison du chocolat',
      },
      query: {
        changeToReadOnly: jest.fn(),
        context: jest.fn().mockReturnValue({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        }),
      },
      trackModifyVenue: jest.fn(),
      venueTypes: [],
      venueLabels: [],
    }
  })

  describe('when editing', () => {

    it('should display contact fields', async ()=> {
      props= {
        ...props,
        venue: {
          ...props.venue,
          contact: {
            email: "contact@venue.com",
            website: "https://my@website.com",
            phoneNumber: "+33102030405",
          }
        },
      }
      const { getContactInputs } = renderVenueEdition({ props })
      const { contactPhoneNumber, contactMail, contactUrl } = await getContactInputs()

      expect(contactPhoneNumber).toBeInTheDocument()
      expect(contactMail).toBeInTheDocument()
      expect(contactUrl).toBeInTheDocument()

      expect(contactPhoneNumber).toBeEnabled()
      expect(contactMail).toBeEnabled()
      expect(contactUrl).toBeEnabled()

      expect(contactUrl).toHaveValue(props.venue.contact.website)
      expect(contactPhoneNumber).toHaveValue(props.venue.contact.phoneNumber)
      expect(contactMail).toHaveValue(props.venue.contact.email)
    })

    it('should be able to edit fields', async ()=> {
      props= {
        ...props,
        venue: {
          ...props.venue,
          contact: {
            email: "contact@venue.com",
            website: "https://my@website.com",
            phoneNumber: "+33102030405",
          }
        },
      }
      const { getContactInputs } = renderVenueEdition({ props })
      const { contactPhoneNumber, contactMail, contactUrl, clearAndFillContact } = await getContactInputs()
      const contactInfos = {
        phone: "0606060606",
        website:"https://some-url-test.com",
        mail:"test@test.com"
      }
      clearAndFillContact(contactInfos)

      expect(contactUrl).toHaveValue(contactInfos.website)
      expect(contactPhoneNumber).toHaveValue(contactInfos.phone)
      expect(contactMail).toHaveValue(contactInfos.mail)

      screen.getByText('Valider').click()

      const expectedRequestParams = {
        ...props.venue,
        contact:  {
          email: contactInfos.mail,
          phoneNumber: contactInfos.phone,
          website: contactInfos.website,
        },
      }

      await waitFor(() => {
        expect(props.handleSubmitRequest).toHaveBeenCalledWith(
          expect.objectContaining({ formValues: expectedRequestParams })
        )
      })
    })

  })

  describe('when read only', () => {
    beforeEach( ()=> {
      jest.spyOn(props.query, 'context').mockImplementation().mockReturnValue({
        readOnly: true,
      })
    })
    it('should display disabled fields', async() => {
      props= {
        ...props,
        venue: {
          ...props.venue,
          contact: {
            email: "contact@venue.com",
            website: "https://my@website.com",
            phoneNumber: "+33102030405",
          }
        },
      }

      const { getContactInputs } = renderVenueEdition({ props })
      const { contactPhoneNumber, contactMail, contactUrl } = await getContactInputs()

      expect(contactPhoneNumber).toBeInTheDocument()
      expect(contactMail).toBeInTheDocument()
      expect(contactUrl).toBeInTheDocument()

      expect(contactPhoneNumber).toBeDisabled()
      expect(contactMail).toBeDisabled()
      expect(contactUrl).toBeDisabled()

      expect(contactUrl).toHaveValue(props.venue.contact.website)
      expect(contactPhoneNumber).toHaveValue(props.venue.contact.phoneNumber)
      expect(contactMail).toHaveValue(props.venue.contact.email)
    })
  })
})
