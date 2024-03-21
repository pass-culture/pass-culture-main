import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik, Form } from 'formik'

import { setInitialFormValues } from 'pages/VenueEdition/setInitialFormValues'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { SubmitButton } from 'ui-kit'
import { defaultGetVenue } from 'utils/collectiveApiFactories'

import { OpeningHoursForm } from '../OpeningHoursForm'

const renderOpeningHoursForm = ({
  onSubmit = vi.fn(),
  venue = defaultGetVenue,
}) => {
  const initialValues: Partial<VenueEditionFormValues> =
    setInitialFormValues(venue)

  return render(
    <Formik initialValues={initialValues} onSubmit={onSubmit}>
      {({ handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          <OpeningHoursForm />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </Form>
      )}
    </Formik>
  )
}

describe('OpeningHoursForm', () => {
  it('should submit the right opening hours hours', async () => {
    const onSubmit = vi.fn()
    renderOpeningHoursForm({ onSubmit })

    expect(
      screen.getByText('Sélectionner vos jours d’ouverture :')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByLabelText('Lundi'))
    expect(screen.getByText('Lundi')).toBeInTheDocument()

    // Reset the afternoon fields
    await userEvent.click(screen.getByText('Ajouter une plage horaire'))
    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 2/),
      '13:37'
    )
    await userEvent.click(screen.getByText('Supprimer la plage horaire'))
    await userEvent.click(screen.getByText('Ajouter une plage horaire'))
    expect(screen.getByLabelText(/Horaire d’ouverture 2/)).toHaveValue('')

    // submit the form with the right values
    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 1/),
      '08:00'
    )
    await userEvent.type(
      screen.getByLabelText(/Horaire de fermeture 1/),
      '12:37'
    )
    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 2/),
      '12:59'
    )
    await userEvent.type(
      screen.getByLabelText(/Horaire de fermeture 2/),
      '16:16'
    )
    await userEvent.click(screen.getByText('Submit'))
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        days: ['monday'],
        monday: {
          afternoonEndingHour: '16:16',
          afternoonStartingHour: '12:59',
          morningEndingHour: '12:37',
          morningStartingHour: '08:00',
        },
        saturday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
        },
        sunday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
        },
        thursday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
        },
        tuesday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
        },
        wednesday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
        },
      }),
      expect.anything()
    )
  })

  it('should display the form with initial values', () => {
    renderOpeningHoursForm({
      venue: {
        ...defaultGetVenue,
        venueOpeningHours: [
          {
            MONDAY: [
              { open: '08:00', close: '12:37' },
              { open: '12:59', close: '16:16' },
            ],
          },
          {
            TUESDAY: undefined,
          },

          {
            WEDNESDAY: [{ open: '09:09', close: '10:02' }],
          },

          {
            THURSDAY: undefined,
          },

          {
            FRIDAY: undefined,
          },
          {
            SATURDAY: undefined,
          },
          {
            SUNDAY: undefined,
          },
        ],
      },
    })
    expect(screen.getByText('Lundi')).toBeInTheDocument()
    expect(screen.getAllByLabelText(/Horaire d’ouverture 1/)[0]).toHaveValue(
      '08:00'
    )
    expect(screen.getAllByLabelText(/Horaire de fermeture 1/)[0]).toHaveValue(
      '12:37'
    )
    expect(screen.getByLabelText(/Horaire d’ouverture 2/)).toHaveValue('12:59')
    expect(screen.getByLabelText(/Horaire de fermeture 2/)).toHaveValue('16:16')
    expect(screen.getByText('Mercredi')).toBeInTheDocument()
    expect(screen.getAllByLabelText(/Horaire d’ouverture 1/)[1]).toHaveValue(
      '09:09'
    )
    expect(screen.getAllByLabelText(/Horaire de fermeture 1/)[1]).toHaveValue(
      '10:02'
    )
  })
})
