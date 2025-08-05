import { render, screen } from '@testing-library/react'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_TYPES,
} from 'commons/core/Offers/constants'
import { FormProvider, useForm } from 'react-hook-form'

import { OfferTypeFormValues } from '../../types'
import { IndividualOfferType } from '../IndividualOfferType'

const OfferTypeIndividualForm = (): JSX.Element => {
  const initialValues: OfferTypeFormValues = {
    offer: {
      offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
      collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
      collectiveOfferSubtypeDuplicate:
        COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
      individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
    },
  }

  const methods = useForm<OfferTypeFormValues>({
    defaultValues: initialValues,
  })

  return (
    <FormProvider {...methods}>
      <IndividualOfferType />
    </FormProvider>
  )
}

vi.mock('react-router', () => ({
  useLocation: () => ({
    pathname: '/offre/creation',
  }),
}))

const renderOfferTypeIndividual = () => {
  return render(<OfferTypeIndividualForm />)
}

describe('OfferTypeIndividual', () => {
  it('should only display macro choices when nothing is on url', async () => {
    renderOfferTypeIndividual()

    expect(await screen.findByText('Votre offre est')).toBeInTheDocument()
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
