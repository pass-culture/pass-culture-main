import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { screen, waitFor } from '@testing-library/react'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { FormProvider, useForm } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'

import {
  ReimbursementFields,
  ReimbursementFieldsProps,
} from '../ReimbursementFields'

const renderReimbursementFields = async (
  defaultProps: ReimbursementFieldsProps,
  options?: RenderWithProvidersOptions
) => {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: {},
      mode: 'onBlur',
    })

    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(() => {})}>
          <ReimbursementFields {...defaultProps} />
          <Button type="submit" isLoading={false}>
            Enregistrer
          </Button>
        </form>
      </FormProvider>
    )
  }

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  renderWithProviders(<Wrapper />, options)
}

describe('ReimbursementFields', () => {
  const venue = {
    ...defaultGetVenue,
    id: 1,
    name: 'fake venue name',
  }
  const otherVenue = {
    id: 2,
    name: 'Offerer Venue',
  } as GetOffererVenueResponseModel
  const offerer = {
    id: 2,
    name: 'fake offerer name',
    managedVenues: [otherVenue],
    hasAvailablePricingPoints: true,
  } as GetOffererResponseModel

  let props: ReimbursementFieldsProps
  beforeEach(() => {
    props = { venue, offerer }
  })

  it('should display banner if offerer has no pricing point and venue has no siret', async () => {
    const offererWithoutPricingPoint = {
      ...offerer,
      hasAvailablePricingPoints: false,
    }
    props.offerer = offererWithoutPricingPoint

    await renderReimbursementFields(props)

    expect(
      screen.queryByText('Créer une structure avec SIRET')
    ).toBeInTheDocument()
  })

  it('should not display pricing point section venue has siret', async () => {
    const venueWithSiret = {
      ...venue,
      siret: '00000000012345',
    }
    props.venue = venueWithSiret

    await renderReimbursementFields(props)

    expect(
      screen.queryByText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      )
    ).not.toBeInTheDocument()
  })

  it('should display pricing point section when venue has no siret', async () => {
    const venueWithoutSiret = {
      ...venue,
      siret: '',
    }

    props.venue = venueWithoutSiret

    await renderReimbursementFields(props)

    expect(
      screen.getByText(
        'Structure avec SIRET utilisée pour le calcul de votre barème de remboursement *'
      )
    ).toBeInTheDocument()
  })
})
