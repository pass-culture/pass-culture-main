import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as hooks from 'commons/hooks/swr/useOfferer'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

window.HTMLElement.prototype.scrollIntoView = vi.fn()

function renderComponent(props: OfferEducationalProps) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory(),
    },
  })
}

describe('screens | OfferEducational : creation offer type step', () => {
  let props: OfferEducationalProps
  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }

  beforeEach(() => {
    vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [venueListItemFactory()],
    })

    props = defaultCreationProps
  })

  it('should display the right fields and titles', async () => {
    renderComponent(props)

    const formatSelect = await screen.findByLabelText('Formats')
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
  })

  describe('domains', () => {
    beforeEach(() => {
      vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)

      props = {
        ...props,
        domainsOptions: [
          {
            label: 'Domain 1',
            id: '1',
            nationalPrograms: [{ id: 1, name: 'nationalProgram1' }],
          },
          { label: 'Domain 2', id: '2', nationalPrograms: [] },
          { label: 'Domain 3', id: '3', nationalPrograms: [] },
        ],
      }
    })

    it('should require user to select a domain', async () => {
      renderComponent(props)
      await userEvent.click(
        await screen.findByLabelText('Domaines artistiques')
      )

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer et continuer' })
      )

      expect(
        screen.getByText('Veuillez renseigner un domaine')
      ).toBeInTheDocument()
    })

    it('should enable user to select domains', async () => {
      renderComponent(props)

      await userEvent.click(
        await screen.findByLabelText('Domaines artistiques')
      )

      await userEvent.click(await screen.findByLabelText(/Domain 2/))

      await userEvent.click(await screen.findByLabelText('Formats'))

      expect(
        screen.queryByText('Veuillez renseigner un domaine')
      ).not.toBeInTheDocument()
    })
  })

  describe('national systems', () => {
    it('should allow user to select national systems', async () => {
      renderComponent(props)

      const domainsSelect = await screen.findByLabelText(
        /Domaines artistiques */
      )
      await userEvent.click(domainsSelect)
      await userEvent.click(await screen.findByText('domain1'))

      const nationalProgramsSelect = await screen.findByLabelText(
        /Dispositif national */
      )
      await userEvent.click(nationalProgramsSelect)
      await userEvent.selectOptions(nationalProgramsSelect, '1')
      await userEvent.tab()

      expect(screen.getByText('nationalProgram1')).toBeInTheDocument()
    })
  })

  describe('formats', () => {
    beforeEach(() => {
      vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
    })

    it('should be able to select a format', async () => {
      renderComponent(props)
      const selectFormat = await screen.findByLabelText('Formats')

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

      expect(titleInput).toHaveValue(title.slice(0, titleMaxLength))
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
  })
})
