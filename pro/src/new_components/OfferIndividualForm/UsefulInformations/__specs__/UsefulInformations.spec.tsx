import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import { SubmitButton } from 'ui-kit'

import UsefulInformations, {
  IUsefulInformationsProps,
} from '../UsefulInformations'
import validationSchema from '../validationSchema'

const renderUsefulInformations = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
  props: IUsefulInformationsProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <UsefulInformations {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('OfferIndividual section: UsefulInformations', () => {
  let initialValues: Partial<IOfferIndividualFormValues>
  let props: IUsefulInformationsProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    const offererNames: TOffererName[] = [
      {
        id: 'AA',
        name: 'Offerer AA',
      },
    ]

    const venueList: TOfferIndividualVenue[] = [
      {
        id: 'AAAA',
        name: 'Venue AAAA',
        managingOffererId: 'AA',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
      {
        id: 'BBBB',
        name: 'Venue BBBB',
        managingOffererId: 'AA',
        isVirtual: true,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
    ]
    initialValues = {
      subCategoryFields: [],
      offererId: '',
      venueId: '',
      subcategoryId: '',
      withdrawalDetails: '',
      withdrawalType: undefined,
      withdrawalDelay: undefined,
      url: '',
    }
    props = {
      offererNames,
      venueList,
      isUserAdmin: false,
      isVenueVirtual: false,
    }
  })

  it('should render the component', async () => {
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    expect(
      await screen.findByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText('Rayonnement national')
    ).not.toBeInTheDocument()
  })

  it('should submit valid form', async () => {
    initialValues.subcategoryId = 'CONCERT'
    initialValues.subCategoryFields = ['withdrawalType']
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    const offererSelect = screen.getByLabelText('Structure')
    await userEvent.selectOptions(offererSelect, 'AA')
    const venueSelect = screen.getByLabelText('Lieu')
    await userEvent.selectOptions(venueSelect, 'AAAA')
    const withEmail = screen.getByLabelText('Envoi par e-mail')
    await userEvent.click(withEmail)

    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: true,
          visual: false,
        },
        isVenueVirtual: false,
        offererId: 'AA',
        subCategoryFields: ['withdrawalType'],
        url: '',
        subcategoryId: 'CONCERT',
        venueId: 'AAAA',
        withdrawalDelay: undefined,
        withdrawalDetails: '',
        withdrawalType: 'by_email',
      },
      expect.anything()
    )
  })

  it('should contain isNational when user is admin', async () => {
    props.isUserAdmin = true
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    await screen.findByRole('heading', { name: 'Informations pratiques' })
    expect(screen.getByLabelText('Rayonnement national')).toBeInTheDocument()
  })

  it('should contain withdrawal ticket informations when subcategory is from specific subCategory', async () => {
    initialValues.subcategoryId = 'CONCERT'
    initialValues.subCategoryFields = ['withdrawalType']
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    await screen.findByRole('heading', { name: 'Informations pratiques' })

    expect(
      screen.getByText('Comment les billets, places seront-ils transmis ?')
    ).toBeInTheDocument()
  })

  it('should not contain withdrawal ticket informations when subcategory is not from specific subCategory', async () => {
    initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    await screen.findByRole('heading', { name: 'Informations pratiques' })

    expect(
      screen.queryByText('Comment les billets, places seront-ils transmis ?')
    ).not.toBeInTheDocument()
  })

  describe('When venue is virtual', () => {
    beforeEach(() => {
      props.isVenueVirtual = true
      props.offerSubCategory = {
        id: 'VIRTUAL_SUB_CATEGORY',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
        isSelectable: true,
      }
      initialValues.subcategoryId = 'VIRTUAL_SUB_CATEGORY'
      initialValues.venueId = 'BBBB'
    })

    it('should submit valid form', async () => {
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      const offererSelect = screen.getByLabelText('Structure')
      await userEvent.selectOptions(offererSelect, 'AA')
      const venueSelect = screen.getByLabelText('Lieu')
      await userEvent.selectOptions(venueSelect, 'BBBB')

      const urlField = await screen.findByLabelText('URL d’accès à l’offre')

      // deactivate type interpolation : https://testing-library.com/docs/ecosystem-user-event/#keyboardtext-options
      await userEvent.type(
        urlField,
        'http://example.com/routes?params={{offerId}'
      )
      await userEvent.click(await screen.findByText('Submit'))

      expect(onSubmit).toHaveBeenCalledWith(
        {
          accessibility: {
            audio: false,
            mental: false,
            motor: false,
            none: true,
            visual: false,
          },
          isVenueVirtual: true,
          offererId: 'AA',
          subCategoryFields: [],
          subcategoryId: 'VIRTUAL_SUB_CATEGORY',
          url: 'http://example.com/routes?params={offerId}',
          venueId: 'BBBB',
          withdrawalDelay: undefined,
          withdrawalDetails: '',
          withdrawalType: undefined,
        },
        expect.anything()
      )
    })

    it('should display url field with errors if needed', async () => {
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      await screen.findByRole('heading', { name: 'Informations pratiques' })

      const offererSelect = screen.getByLabelText('Structure')
      await userEvent.selectOptions(offererSelect, 'AA')
      const venueSelect = screen.getByLabelText('Lieu')
      await userEvent.selectOptions(venueSelect, 'BBBB')

      const urlField = await screen.findByLabelText('URL d’accès à l’offre')
      await userEvent.click(urlField)
      await userEvent.tab()

      expect(
        await screen.findByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).toBeInTheDocument()

      await userEvent.type(
        urlField,
        'http://example.com/routes?params={offerId}'
      )
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).not.toBeInTheDocument()

      await userEvent.clear(urlField)
      await userEvent.type(urlField, 'FAKE_URL')
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).toBeInTheDocument()
    })
  })

  describe('banners', () => {
    it('should display not reimbursment banner when subcategory is not reimbursed', async () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
        isSelectable: true,
      }
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      await screen.findByRole('heading', { name: 'Informations pratiques' })

      expect(
        screen.queryByText(
          'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
        )
      ).toBeInTheDocument()
    })

    it('should not display not reimbursment banner when subcategory is reimbursed', async () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.BOOK,
        isSelectable: true,
      }
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      await screen.findByRole('heading', { name: 'Informations pratiques' })

      expect(
        screen.queryByText(
          'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
        )
      ).not.toBeInTheDocument()
    })

    it('should display withdrawal banner when subcategory is on physical thing (not event, not virtual)', async () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      }
      props.isVenueVirtual = false
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      await screen.findByRole('heading', { name: 'Informations pratiques' })

      expect(
        screen.queryByText(
          'La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos CGU.'
        )
      ).toBeInTheDocument()
    })

    it('should not display withdrawal banner when subcategory is an event', async () => {
      initialValues.subcategoryId = 'ANOTHER_SUB_CATEGORY'
      props.offerSubCategory = {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      }
      props.isVenueVirtual = false
      renderUsefulInformations({
        initialValues,
        onSubmit,
        props,
      })

      await screen.findByRole('heading', { name: 'Informations pratiques' })

      expect(
        screen.queryByText(
          'La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos CGU.'
        )
      ).not.toBeInTheDocument()
    })
  })
})
