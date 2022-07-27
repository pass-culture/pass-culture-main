import '@testing-library/jest-dom'

// TODO: move this into components/pages/Offerers/Offerer/VenueV1/__test-utils__

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'

import VenueLabel from 'components/pages/Offerers/Offerer/VenueV1/ValueObjects/VenueLabel'
import VenueType from 'components/pages/Offerers/Offerer/VenueV1/ValueObjects/VenueType'
import * as helpers from 'components/pages/Offerers/Offerer/VenueV1/VenueCreation/__specs__/helpers'
import { humanizeSiret } from 'core/Venue'
import { configureTestStore } from 'store/testUtils'

import IdentifierFields from '../IdentifierFields'
import getLabelFromList from '../utils/getLabelFromList'

const renderIdentifierFields = async ({
  props,
  formValues = {},
  storeOverride = {},
}) => {
  const store = configureTestStore(storeOverride)
  const rtlReturns = render(
    <Provider store={store}>
      <Form initialValues={formValues} name="venue" onSubmit={() => null}>
        {() => <IdentifierFields {...props} />}
      </Form>
    </Provider>
  )
  await screen.findByText('Informations lieu')
  return rtlReturns
}

describe('src | components | pages | Venue | fields | IdentifierFields', () => {
  let props
  let formValues

  beforeEach(() => {
    props = {
      // default component props
      fieldReadOnlyBecauseFrozenFormSiret: false,
      formSiret: null,
      initialSiret: null,
      isCreatedEntity: false,
      isDirtyFieldBookingEmail: false,
      readOnly: true,
      venueIsVirtual: false,
      venueLabelId: null,
      venueTypeCode: null,

      // some mandatory props
      isEntrepriseApiDisabled: false,
      isModifiedEntity: true,
      venueTypes: [
        new VenueType({
          id: 'TYPE_ID',
          label: 'Venue type label',
        }),
        new VenueType({
          id: 'OTHER_TYPE_ID',
          label: 'Other venue type label',
        }),
      ],
      venueLabels: [
        new VenueLabel({
          id: 'LABEL_ID',
          label: 'Venue Label label',
        }),
        new VenueLabel({
          id: 'OTHER_LABEL_ID',
          label: 'Other venue Label label',
        }),
      ],
    }

    formValues = {}
  })

  // on venue edition page, we first arrive on a visualisation mode
  // where all form fields are readonly or replace by div and span
  describe('visualisation mode', () => {
    beforeEach(() => {
      formValues = {
        siret: '12345678912345',
        name: 'Venue name',
        publicName: 'Venue publicName',
        bookingEmail: 'booking@email.app',
        venueTypeCode: 'OTHER_TYPE_ID',
        venueLabelId: 'OTHER_LABEL_ID',
        description: 'Venue description',
      }
      props = {
        ...props,
        readOnly: true,

        fieldReadOnlyBecauseFrozenFormSiret: false,
        formSiret: '12345678912345',
        initialSiret: '12345678912345',
        isCreatedEntity: false,
        isDirtyFieldBookingEmail: false,
        venueIsVirtual: false,
        venueTypeCode: 'OTHER_TYPE_ID',
        venueLabelId: 'OTHER_LABEL_ID',
      }
    })

    it('should display disabled form', async () => {
      await renderIdentifierFields({ props, formValues })

      const siretField = await helpers.findVenueInputForField('siret')
      const nameField = await helpers.findVenueInputForField('name')
      const publicNameField = await helpers.findVenueInputForField('publicName')
      // helpers get element with edition mode labels.
      const bookingEmailField = await screen.findByLabelText('Mail', {
        exact: false,
      })
      const venueTypeCodeField = await helpers.queryVenueInputForField(
        'venueTypeCode'
      )
      const venueLabelIdField = helpers.queryVenueInputForField('venueLabelId')
      const descriptionField = await helpers.findVenueInputForField(
        'description'
      )

      expect(siretField).toBeDisabled()
      expect(nameField).toBeDisabled()
      expect(publicNameField).toBeDisabled()
      expect(bookingEmailField).toBeDisabled()
      expect(descriptionField).toBeDisabled()

      // select elements are replace with spans
      expect(venueTypeCodeField).not.toBeInTheDocument()
      expect(venueLabelIdField).not.toBeInTheDocument()
    })

    it('should displayed informations form form values', async () => {
      await renderIdentifierFields({ props, formValues })
      const displayedValues = {
        siret: humanizeSiret(formValues['siret']),
        name: formValues['name'],
        publicName: formValues['publicName'],
        bookingEmail: formValues['bookingEmail'],
        venueTypeCode: getLabelFromList(
          props.venueTypes,
          formValues['venueTypeCode']
        ),
        venueLabelId: getLabelFromList(
          props.venueLabels,
          formValues['venueLabelId']
        ),
        description: formValues['description'],
      }
      expect(
        screen.getByDisplayValue(displayedValues['siret'])
      ).toBeInTheDocument()
      expect(
        screen.getByDisplayValue(displayedValues['name'])
      ).toBeInTheDocument()
      expect(
        screen.getByDisplayValue(displayedValues['publicName'])
      ).toBeInTheDocument()
      expect(
        screen.getByDisplayValue(displayedValues['bookingEmail'])
      ).toBeInTheDocument()
      expect(
        screen.getByDisplayValue(displayedValues['description'])
      ).toBeInTheDocument()
      expect(
        screen.getByText(displayedValues['venueTypeCode'])
      ).toBeInTheDocument()
      expect(
        screen.getByText(displayedValues['venueLabelId'])
      ).toBeInTheDocument()
    })
  })

  describe('edition mode for venue creation', () => {
    beforeEach(() => {
      formValues = {}
      props = {
        ...props,
        readOnly: false,
        isCreatedEntity: true,

        fieldReadOnlyBecauseFrozenFormSiret: false,
        formSiret: null,
        initialSiret: null,
        isDirtyFieldBookingEmail: false,
        venueIsVirtual: false,
        venueLabelId: null,
        venueTypeCode: null,
      }
    })

    it('should render form elements', async () => {
      await renderIdentifierFields({ props, formValues })

      const siretField = await helpers.findVenueInputForField(
        'siret',
        props.isCreatedEntity
      )
      const nameField = await helpers.findVenueInputForField('name')
      const publicNameField = await helpers.findVenueInputForField('publicName')
      const bookingEmailField = await helpers.findVenueInputForField(
        'bookingEmail'
      )
      const venueTypeCodeField = await helpers.findVenueInputForField(
        'venueTypeCode'
      )
      const venueLabelIdField = await helpers.findVenueInputForField(
        'venueLabelId'
      )
      const descriptionField = await helpers.findVenueInputForField(
        'description'
      )

      expect(siretField).toBeEnabled()
      expect(nameField).toBeEnabled()
      expect(publicNameField).toBeEnabled()
      expect(bookingEmailField).toBeEnabled()
      expect(descriptionField).toBeEnabled()
      expect(venueTypeCodeField).toBeEnabled()
      expect(venueLabelIdField).toBeEnabled()

      expect(nameField).toBeRequired()
      expect(venueTypeCodeField).toBeRequired()
      expect(bookingEmailField).toBeRequired()
      expect(siretField).toBeRequired()
      expect(publicNameField).not.toBeRequired()
      expect(descriptionField).not.toBeRequired()
      expect(venueLabelIdField).not.toBeRequired()

      expect(siretField).toHaveValue('')
      expect(nameField).toHaveValue('')
      expect(publicNameField).toHaveValue('')
      expect(bookingEmailField).toHaveValue('')
      expect(descriptionField).toHaveValue('')
      expect(venueTypeCodeField).toHaveValue('')
      expect(venueLabelIdField).toHaveValue('')
    })
  })

  describe('edition mode for venue edition', () => {
    beforeEach(() => {
      formValues = {
        siret: '12345678912345',
        name: 'Venue name',
        publicName: 'Venue publicName',
        bookingEmail: 'booking@email.app',
        venueTypeCode: 'OTHER_TYPE_ID',
        venueLabelId: 'OTHER_LABEL_ID',
        description: 'Venue description',
      }
      props = {
        ...props,
        readOnly: false,
        isCreatedEntity: true,

        fieldReadOnlyBecauseFrozenFormSiret: true,
        formSiret: '00000000000027',
        initialSiret: '00000000000027',
        isDirtyFieldBookingEmail: false,
        venueIsVirtual: false,
        venueLabelId: null,
        venueTypeCode: null,
      }
    })

    it('should render form elements', async () => {
      await renderIdentifierFields({ props, formValues })

      const siretField = await helpers.findVenueInputForField(
        'siret',
        props.isCreatedEntity
      )
      const nameField = await helpers.findVenueInputForField('name')
      const publicNameField = await helpers.findVenueInputForField('publicName')
      const bookingEmailField = await helpers.findVenueInputForField(
        'bookingEmail'
      )
      const venueTypeCodeField = await helpers.findVenueInputForField(
        'venueTypeCode'
      )
      const venueLabelIdField = await helpers.findVenueInputForField(
        'venueLabelId'
      )
      const descriptionField = await helpers.findVenueInputForField(
        'description'
      )

      // Some field cannot be edited for existing venues
      expect(siretField).toBeDisabled()
      expect(nameField).toBeDisabled()

      expect(publicNameField).toBeEnabled()
      expect(bookingEmailField).toBeEnabled()
      expect(descriptionField).toBeEnabled()
      expect(venueTypeCodeField).toBeEnabled()
      expect(venueLabelIdField).toBeEnabled()

      expect(nameField).toBeRequired()
      expect(venueTypeCodeField).toBeRequired()
      expect(bookingEmailField).toBeRequired()
      expect(siretField).toBeRequired()
      expect(publicNameField).not.toBeRequired()
      expect(descriptionField).not.toBeRequired()
      expect(venueLabelIdField).not.toBeRequired()

      expect(siretField).toHaveValue(humanizeSiret(formValues.siret))
      expect(nameField).toHaveValue(formValues.name)
      expect(publicNameField).toHaveValue(formValues.publicName)
      expect(bookingEmailField).toHaveValue(formValues.bookingEmail)
      expect(descriptionField).toHaveValue(formValues.description)
      expect(venueTypeCodeField).toHaveValue(formValues.venueTypeCode)
      expect(venueLabelIdField).toHaveValue(formValues.venueLabelId)
    })
  })
})
