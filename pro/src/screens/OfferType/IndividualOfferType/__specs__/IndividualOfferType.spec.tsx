import { render, screen } from '@testing-library/react'
import { FormikProvider, useFormik } from 'formik'

import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_TYPES,
} from 'core/Offers/constants'
import { OfferTypeFormValues } from 'screens/OfferType/types'

import { IndividualOfferType } from '../IndividualOfferType'

const TestForm = (): JSX.Element => {
  const initialValues: OfferTypeFormValues = {
    offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
    collectiveOfferSubtypeDuplicate:
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
    individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
  }

  const formik = useFormik<OfferTypeFormValues>({
    initialValues: initialValues,
    onSubmit: vi.fn(),
  })

  return (
    <FormikProvider value={formik}>
      <IndividualOfferType />
    </FormikProvider>
  )
}

const renderOfferTypeIndividual = () => {
  return render(<TestForm />)
}

describe('OfferTypeIndividual', () => {
  it('should only display macro choices when user is admin and nothing is on url', async () => {
    renderOfferTypeIndividual()

    expect(await screen.findByText('Votre offre est :')).toBeInTheDocument()
    expect(await screen.findByText('Un bien physique')).toBeInTheDocument()
    expect(await screen.findByText('Un bien numérique')).toBeInTheDocument()
    expect(
      await screen.findByText('Un évènement physique daté')
    ).toBeInTheDocument()
    expect(
      await screen.findByText('Un évènement numérique daté')
    ).toBeInTheDocument()
  })
})
