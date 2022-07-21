import '@testing-library/jest-dom'

import * as yup from 'yup'

import { AccessiblityEnum, IAccessibiltyFormValues } from 'core/shared'
import { render, screen } from '@testing-library/react'

import { Accessibility } from 'new_components/OfferIndividualForm/Accessibility'
import { Formik } from 'formik'
import { IVenueProps } from '../Venue'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'
import { Venue } from '..'
import userEvent from '@testing-library/user-event'

interface IInitialValues {
  offererId: string
  venueId: string
  accessibility: IAccessibiltyFormValues
}

const renderVenue = async ({
  initialValues,
  onSubmit = jest.fn(),
  venueProps,
}: {
  initialValues: IInitialValues
  onSubmit: () => void
  venueProps: IVenueProps
}) => {
  const rtlReturn = await render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object()}
    >
      <>
        <Venue {...venueProps} />
        <Accessibility />
      </>
    </Formik>
  )

  const selectVenue = screen.getByLabelText('Lieu')
  const checkboxNone = screen.getByLabelText('Non accessible', {
    exact: false,
  })
  const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })
  const checkboxMental = screen.getByLabelText('Psychique ou cognitif', {
    exact: false,
  })
  const checkboxMoteur = screen.getByLabelText('Moteur', { exact: false })
  const checkboxAuditif = screen.getByLabelText('Auditif', { exact: false })

  return {
    ...rtlReturn,
    selectVenue,
    checkboxNone,
    checkboxVisuel,
    checkboxMental,
    checkboxMoteur,
    checkboxAuditif,
  }
}

describe('OfferIndividual section: venue', () => {
  let initialValues: IInitialValues
  let venueProps: IVenueProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    const offererNames: TOffererName[] = [
      {
        id: 'AA',
        name: 'Offerer AA',
      },
    ]

    const venueAccessible: TOfferIndividualVenue = {
      id: 'AAAA',
      name: 'Venue AAAA',
      managingOffererId: 'AA',
      isVirtual: false,
      withdrawalDetails: '',
      accessibility: {
        visual: false,
        mental: true,
        audio: true,
        motor: false,
        none: false,
      },
    }
    const venueNotAccessible: TOfferIndividualVenue = {
      id: 'AABB',
      name: 'Venue AABB',
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
    }
    const venueList: TOfferIndividualVenue[] = [
      venueAccessible,
      venueNotAccessible,
    ]

    initialValues = {
      offererId: 'AA',
      venueId: '',
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: false,
      },
    }
    venueProps = {
      offererNames,
      venueList,
    }
  })

  it('should fill accessibilities when venue change', async () => {
    const {
      selectVenue,
      checkboxNone,
      checkboxVisuel,
      checkboxMental,
      checkboxMoteur,
      checkboxAuditif,
    } = await renderVenue({
      initialValues,
      onSubmit,
      venueProps,
    })
    await screen.findByRole('heading', { name: 'Accessibilité' })

    await userEvent.selectOptions(selectVenue, 'AAAA')
    expect(checkboxVisuel).not.toBeChecked()
    expect(checkboxMental).toBeChecked()
    expect(checkboxAuditif).toBeChecked()
    expect(checkboxMoteur).not.toBeChecked()
    expect(checkboxNone).not.toBeChecked()

    await userEvent.selectOptions(selectVenue, 'AABB')
    expect(checkboxVisuel).not.toBeChecked()
    expect(checkboxMental).not.toBeChecked()
    expect(checkboxAuditif).not.toBeChecked()
    expect(checkboxMoteur).not.toBeChecked()
    expect(checkboxNone).toBeChecked()

    await userEvent.click(checkboxVisuel)
    expect(checkboxNone).not.toBeChecked()
    expect(checkboxVisuel).toBeChecked()
  })
})
