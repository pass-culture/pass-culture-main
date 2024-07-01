import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : creation offer type step', () => {
  let props: OfferEducationalProps
  let store: any

  beforeEach(() => {
    props = defaultCreationProps
  })

  it('should display the right fields and titles', async () => {
    renderWithProviders(<OfferEducational {...props} />)

    const formatSelect = await screen.findByLabelText('Format *')
    expect(formatSelect).toBeInTheDocument()
    expect(formatSelect).toBeEnabled()
    expect(formatSelect).toHaveValue('')

    const titleInput = await screen.findByLabelText('Titre de l’offre *')
    expect(titleInput).toBeEnabled()
    expect(titleInput).toHaveValue('')
    expect(titleInput.getAttribute('placeholder')).toBeNull()

    expect(await screen.findByTestId('counter-title')).toHaveTextContent(
      '0/110'
    )

    const descriptionTextArea = await screen.findByLabelText(/Description */)
    expect(descriptionTextArea).toBeEnabled()
    expect(descriptionTextArea).toHaveValue('')
    expect(descriptionTextArea.getAttribute('placeholder')).toBe(
      'Détaillez ici votre projet et son interêt pédagogique.'
    )
    expect(await screen.findByTestId('counter-description')).toHaveTextContent(
      '0/1000'
    )

    const durationInput = screen.getByLabelText(/Durée/)
    expect(durationInput).toBeInTheDocument()
    expect(durationInput).toBeEnabled()
    expect(durationInput).toHaveValue('')
    expect(durationInput.getAttribute('placeholder')).toBe('HH:MM')
  })

  describe('domains', () => {
    beforeEach(() => {
      props = {
        ...props,
        domainsOptions: [
          { label: 'Domain 1', value: 1 },
          { label: 'Domain 2', value: 2 },
          { label: 'Domain 3', value: 3 },
        ],
      }
    })

    it('should require user to select a domain', async () => {
      renderWithProviders(<OfferEducational {...props} />, {
        storeOverrides: store,
      })
      await userEvent.click(
        await screen.findByLabelText(/Domaine artistique et culturel */)
      )

      await userEvent.click(screen.getByLabelText(/Format */))

      expect(
        screen.getByText('Veuillez renseigner un domaine')
      ).toBeInTheDocument()
    })

    it('should enable user to select domains', async () => {
      renderWithProviders(<OfferEducational {...props} />, {
        storeOverrides: store,
      })

      await userEvent.click(
        await screen.findByLabelText(/Domaine artistique et culturel */)
      )

      await userEvent.click(await screen.findByLabelText(/Domain 2/))

      await userEvent.click(screen.getByLabelText(/Format */))

      expect(
        screen.queryByText('Veuillez renseigner un domaine')
      ).not.toBeInTheDocument()
    })
  })

  describe('national systems', () => {
    it('should allow user to select national systems', async () => {
      const overridedProps = {
        ...props,
        nationalPrograms: [
          { value: 1, label: 'Marseille en grand' },
          { value: 4, label: 'Olympiades' },
        ],
      }
      renderWithProviders(<OfferEducational {...overridedProps} />, {
        storeOverrides: store,
      })
      const nationalProgramsSelect = await screen.findByLabelText(
        /Dispositif national */
      )
      await userEvent.click(nationalProgramsSelect)
      await userEvent.selectOptions(nationalProgramsSelect, '4')
      await userEvent.tab()

      expect(screen.getByText('Olympiades')).toBeInTheDocument()
    })
  })

  describe('formats', () => {
    it('should be able to select a format', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      const selectFormat = await screen.findByRole('combobox', {
        name: 'Format *',
      })

      await userEvent.click(selectFormat)

      await userEvent.click(
        screen.getByRole('checkbox', { name: 'Atelier de pratique' })
      )

      expect(
        screen.getByRole('button', { name: /Atelier de pratique/ })
      ).toBeInTheDocument()
    })
  })

  describe('title, description and duration inputs', () => {
    it('should require a title with less than 110 chars (and truncate longer strings)', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      const titleMaxLength = 110

      const titleInput = await screen.findByLabelText('Titre de l’offre *')
      expect(titleInput).toHaveValue('')
      expect(screen.getByTestId('counter-title')).toHaveTextContent(
        `0/${titleMaxLength}`
      )

      await userEvent.click(titleInput)
      await userEvent.tab()

      await waitFor(() =>
        expect(
          screen.getByText('Veuillez renseigner un titre')
        ).toBeInTheDocument()
      )

      const title =
        'a valid title ' + Array.from({ length: 50 }).map(() => 'test ')
      await userEvent.type(titleInput, title)

      expect(screen.getByTestId('counter-title')).toHaveTextContent(
        `${titleMaxLength}/${titleMaxLength}`
      )

      expect(titleInput.getAttribute('value')).toHaveLength(titleMaxLength)
    })

    it('should require a description with less than 1000 chars (and truncate longer strings)', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      const descMaxLength = 1000

      const description = await screen.findByLabelText(/Description */)
      expect(description).toHaveValue('')
      expect(screen.getByTestId('counter-description')).toHaveTextContent(
        `0/${descMaxLength}`
      )

      const descriptionString =
        'my description that is valid' +
        Array.from({ length: 50 }).map(() => 'description pour tester')

      // hack - to be fixed
      await userEvent.click(description)
      await userEvent.paste(descriptionString)

      expect(descriptionString).toContain(description.textContent)

      expect(screen.getByTestId('counter-description')).toHaveTextContent(
        `${descMaxLength}/${descMaxLength}`
      )

      expect(description.textContent).toHaveLength(descMaxLength)
    })

    it('should have a duration field with a format of hh:mm', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      const duration = await screen.findByLabelText(/Durée */)
      expect(duration).toHaveValue('')

      await userEvent.type(duration, 'bad String')

      await waitFor(() => expect(duration).toHaveValue('bad String'))

      await userEvent.click(duration)
      await userEvent.tab()

      expect(
        screen.getByText(
          'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
        )
      ).toBeInTheDocument()

      await userEvent.clear(duration)
      await userEvent.type(duration, '2:30')

      expect(duration).toHaveValue('2:30')

      expect(
        screen.queryByText(
          'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
        )
      ).not.toBeInTheDocument()
    })
  })
})
