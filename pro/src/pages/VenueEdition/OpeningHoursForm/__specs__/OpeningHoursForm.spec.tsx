import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik, Form } from 'formik'

import { setInitialFormValues } from 'pages/VenueEdition/setInitialFormValues'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { getValidationSchema } from 'pages/VenueEdition/validationSchema'
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
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={getValidationSchema(false)}
    >
      <Form>
        <OpeningHoursForm />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
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
          isAfternoonOpen: true,
        },
        saturday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
          isAfternoonOpen: false,
        },
        sunday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
          isAfternoonOpen: false,
        },
        thursday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
          isAfternoonOpen: false,
        },
        tuesday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
          isAfternoonOpen: false,
        },
        wednesday: {
          afternoonEndingHour: '',
          afternoonStartingHour: '',
          morningEndingHour: '',
          morningStartingHour: '',
          isAfternoonOpen: false,
        },
      }),
      expect.anything()
    )
  })

  it('should display the form with initial values', () => {
    renderOpeningHoursForm({
      venue: {
        ...defaultGetVenue,
        openingHours: {
          MONDAY: [
            { open: '08:00', close: '12:37' },
            { open: '12:59', close: '16:16' },
          ],
          TUESDAY: undefined,
          WEDNESDAY: [{ open: '09:09', close: '10:02' }],
          THURSDAY: undefined,
          FRIDAY: undefined,
          SATURDAY: undefined,
          SUNDAY: undefined,
        },
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

  it('should display errors', async () => {
    renderOpeningHoursForm({})

    await userEvent.click(screen.getByLabelText('Lundi'))
    await userEvent.click(screen.getByText('Ajouter une plage horaire'))

    await userEvent.click(screen.getByText('Submit'))

    expect(
      screen.getAllByText('Veuillez renseigner une heure de début')
    ).toHaveLength(2)
    expect(
      screen.getAllByText('Veuillez renseigner une heure de fin')
    ).toHaveLength(2)

    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 1/),
      '18:00'
    )
    await userEvent.type(
      screen.getByLabelText(/Horaire de fermeture 1/),
      '10:30'
    )
    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 2/),
      '18:00'
    )
    await userEvent.type(
      screen.getByLabelText(/Horaire de fermeture 2/),
      '10:00'
    )

    expect(
      screen.getAllByText(
        "L'heure de fin doit être supérieure à l'heure de début"
      )
    ).toHaveLength(2)
  })

  it('should set min value for ending hours', async () => {
    renderOpeningHoursForm({})

    await userEvent.click(screen.getByLabelText('Lundi'))
    await userEvent.click(screen.getByText('Ajouter une plage horaire'))

    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 1/),
      '10:00'
    )
    expect(screen.getByLabelText(/Horaire de fermeture 1/)).toHaveAttribute(
      'min',
      '10:00'
    )

    await userEvent.type(
      screen.getByLabelText(/Horaire de fermeture 1/),
      '12:00'
    )
    expect(screen.getByLabelText(/Horaire d’ouverture 2/)).toHaveAttribute(
      'min',
      '12:00'
    )

    await userEvent.type(
      screen.getByLabelText(/Horaire d’ouverture 2/),
      '18:00'
    )
    expect(screen.getByLabelText(/Horaire de fermeture 2/)).toHaveAttribute(
      'min',
      '18:00'
    )
  })

  it('should show all errors', async () => {
    renderOpeningHoursForm({})

    await userEvent.click(screen.getByLabelText('Mardi'))
    await userEvent.click(screen.getByLabelText('Mercredi'))
    await userEvent.click(screen.getByLabelText('Jeudi'))

    await userEvent.click(screen.getByText('Submit'))

    expect(
      screen.getAllByText('Veuillez renseigner une heure de début')
    ).toHaveLength(3)
    expect(
      screen.getAllByText('Veuillez renseigner une heure de fin')
    ).toHaveLength(3)
  })
})
