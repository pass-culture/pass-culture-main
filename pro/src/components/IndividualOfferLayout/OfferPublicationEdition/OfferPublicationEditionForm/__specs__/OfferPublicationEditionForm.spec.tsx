import { screen, waitFor } from '@testing-library/react'
import { addDays } from 'date-fns'

import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import {
  OfferPublicationEditionForm,
  OfferPublicationEditionFormProps,
} from '../OfferPublicationEditionForm'

function renderOfferPublicationEditionForm(
  props: OfferPublicationEditionFormProps
) {
  return renderWithProviders(
    <DialogBuilder defaultOpen title="test">
      <OfferPublicationEditionForm {...props} />
    </DialogBuilder>
  )
}

describe('OfferPublicationEditionForm', () => {
  it('should render the form', async () => {
    renderOfferPublicationEditionForm({
      offer: getIndividualOfferFactory({
        publicationDatetime: null,
        bookingAllowedDatetime: null,
      }),
      onSubmit: () => {},
    })

    expect(
      screen.getAllByRole('radiogroup', {
        name: 'Quand votre offre doit-elle être publiée dans l’application ?',
      })[0]
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: 'Mettre en pause l’offre' })
      ).toBeInTheDocument()
    })
  })

  it('should disable the form if the pause toggle is on', async () => {
    renderOfferPublicationEditionForm({
      offer: getIndividualOfferFactory({
        publicationDatetime: null,
        bookingAllowedDatetime: null,
      }),
      onSubmit: () => {},
    })

    await waitFor(() => {
      expect(
        screen.getByRole('radio', {
          name: 'Publier plus tard L’offre restera secrète pour le public jusqu’à sa publication.',
        })
      ).toBeDisabled()
    })

    expect(
      screen.getByRole('radio', {
        name: /Rendre réservable plus tard/,
      })
    ).toBeDisabled()
  })

  it('should pre-fill the publication date', async () => {
    const publicationDate = addDays(new Date(), 2).toISOString()

    //  The publication date can only have a time every 15 minutes : 12:00, 12:15, 12:30...
    const publicationDateFomatted = `${publicationDate.split('T')[0]}T12:00:00Z`

    renderOfferPublicationEditionForm({
      offer: getIndividualOfferFactory({
        publicationDatetime: publicationDateFomatted,
        bookingAllowedDatetime: null,
      }),
      onSubmit: () => {},
    })

    await waitFor(() => {
      expect(
        screen.getByRole('radio', {
          name: 'Publier plus tard L’offre restera secrète pour le public jusqu’à sa publication.',
        })
      ).toBeEnabled()
    })

    expect(screen.getByLabelText('Date *')).toHaveValue()
    expect(screen.getByLabelText('Heure *')).toHaveValue()
  })

  it('should pre-fill the booking allowed date', async () => {
    const bookingAllowedDate = addDays(new Date(), 2).toISOString()

    //  The booking allowed date can only have a time every 15 minutes : 12:00, 12:15, 12:30...
    const bookingAllowedDateFormatted = `${bookingAllowedDate.split('T')[0]}T12:00:00Z`

    renderOfferPublicationEditionForm({
      offer: getIndividualOfferFactory({
        publicationDatetime: bookingAllowedDateFormatted,
        bookingAllowedDatetime: null,
      }),
      onSubmit: () => {},
    })

    await waitFor(() => {
      expect(
        screen.getByRole('radio', {
          name: /Rendre réservable plus tard/,
        })
      ).toBeEnabled()
    })

    expect(screen.getByLabelText('Date *')).toHaveValue()
    expect(screen.getByLabelText('Heure *')).toHaveValue()
  })
})
