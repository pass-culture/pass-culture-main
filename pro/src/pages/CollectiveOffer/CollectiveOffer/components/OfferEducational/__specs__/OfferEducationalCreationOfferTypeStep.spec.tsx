import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

function renderComponent(props: OfferEducationalProps) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: { selectedOffererId: 1, offererNames: [] },
    },
  })
}

describe('screens | OfferEducational : creation offer type step', () => {
  let props: OfferEducationalProps

  beforeEach(() => {
    props = defaultCreationProps
  })

  it('should display the right fields and titles', async () => {
    renderComponent(props)

    const formatSelect = await screen.findByLabelText(
      'Ajoutez un ou plusieurs formats *'
    )
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

    const descriptionTextArea = await screen.findByLabelText(
      /Décrivez ici votre projet et son interêt pédagogique */
    )
    expect(descriptionTextArea).toBeEnabled()
    expect(descriptionTextArea).toHaveValue('')

    expect(await screen.findByTestId('counter-description')).toHaveTextContent(
      '0/1500'
    )

    const durationInput = screen.getByLabelText(
      /Indiquez la durée de l’évènement/
    )
    expect(durationInput).toBeInTheDocument()
    expect(durationInput).toBeEnabled()
    expect(durationInput).toHaveValue('')
    const durationInputDesc = screen.getByTestId('description-duration')
    expect(durationInputDesc).toHaveTextContent('Format : HH:MM')
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
      renderComponent(props)
      await userEvent.click(
        await screen.findByLabelText(
          /Ajoutez un ou plusieurs domaines artistiques */
        )
      )

      await userEvent.click(
        screen.getByLabelText(/Ajoutez un ou plusieurs formats */)
      )

      expect(
        screen.getByText('Veuillez renseigner un domaine')
      ).toBeInTheDocument()
    })

    it('should enable user to select domains', async () => {
      renderComponent(props)

      await userEvent.click(
        await screen.findByLabelText(
          /Ajoutez un ou plusieurs domaines artistiques */
        )
      )

      await userEvent.click(await screen.findByLabelText(/Domain 2/))

      await userEvent.click(
        screen.getByLabelText(/Ajoutez un ou plusieurs formats */)
      )

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
      renderComponent(overridedProps)
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
      renderComponent(props)
      const selectFormat = await screen.findByRole('combobox', {
        name: 'Ajoutez un ou plusieurs formats *',
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
      renderComponent(props)
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

    it('should require a description with less than 1500 chars (and truncate longer strings)', async () => {
      renderComponent(props)
      const descMaxLength = 1500

      const description = await screen.findByLabelText(
        /Décrivez ici votre projet et son interêt pédagogique */
      )
      expect(description).toHaveValue('')
      expect(screen.getByTestId('counter-description')).toHaveTextContent(
        `0/${descMaxLength}`
      )

      const descriptionString =
        'my description that is valid' +
        Array.from({ length: 70 }).map(() => 'description pour tester')

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
      renderComponent(props)
      const duration = await screen.findByLabelText(
        /Indiquez la durée de l’évènement */
      )
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
