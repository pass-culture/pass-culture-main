import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays, subDays } from 'date-fns'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  getPatchOfferPayloadFromFormValues,
  OfferPublicationEdition,
  type OfferPublicationEditionProps,
} from './OfferPublicationEdition'
import type { EventPublicationEditionFormValues } from './OfferPublicationEditionForm/types'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
  },
}))

function renderOfferPublicationEdition(props: OfferPublicationEditionProps) {
  return renderWithProviders(
    <>
      <OfferPublicationEdition {...props} />
      <SnackBarContainer />
    </>
  )
}

describe('OfferPublicationEdition', () => {
  it('should open and close the drawer', async () => {
    renderOfferPublicationEdition({ offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByRole('button', { name: 'Modifier' }))

    expect(screen.getByText('Publication et réservation')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(
      screen.queryByText('Publication et réservation')
    ).not.toBeInTheDocument()
  })

  it('should patch the offer when submitting the form', async () => {
    const patchSpy = vi.spyOn(api, 'patchOffer')

    renderOfferPublicationEdition({ offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByRole('button', { name: 'Modifier' }))

    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(patchSpy).toHaveBeenCalledOnce()
  })

  it('should display an error message if the patch fails', async () => {
    vi.spyOn(api, 'patchOffer').mockRejectedValueOnce('error')

    renderOfferPublicationEdition({ offer: getIndividualOfferFactory() })

    await userEvent.click(screen.getByRole('button', { name: 'Modifier' }))

    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(
      screen.getByText(
        'Une erreur est survenue lors de la modification de l’offre'
      )
    ).toBeInTheDocument()
  })

  it('should format the payload to patch the offer', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      isEvent: true,
      publicationDatetime: subDays(new Date(), 1).toISOString(),
      bookingAllowedDatetime: undefined,
    })

    const values: EventPublicationEditionFormValues = {
      isPaused: false,
      publicationMode: 'now',
      bookingAllowedMode: 'now',
    }

    const tomorrow = addDays(new Date(), 1).toISOString()
    const [tomorrowDate, tomorrowTime] = tomorrow.split('.')[0].split('T')

    expect(getPatchOfferPayloadFromFormValues(offer, values)).toEqual(
      expect.objectContaining({
        publicationDatetime: 'now',
        bookingAllowedDatetime: null,
      })
    )

    expect(
      getPatchOfferPayloadFromFormValues(offer, {
        ...values,
        publicationMode: 'later',
        publicationDate: tomorrowDate,
        publicationTime: tomorrowTime,
      })
    ).toEqual(
      expect.objectContaining({
        bookingAllowedDatetime: null,
        publicationDatetime: expect.stringContaining(tomorrowDate),
      })
    )

    expect(
      getPatchOfferPayloadFromFormValues(offer, {
        ...values,
        bookingAllowedMode: 'later',
        bookingAllowedDate: tomorrowDate,
        bookingAllowedTime: tomorrowTime,
      })
    ).toEqual(
      expect.objectContaining({
        publicationDatetime: 'now',
        bookingAllowedDatetime: expect.stringContaining(tomorrowDate),
      })
    )
  })
})
