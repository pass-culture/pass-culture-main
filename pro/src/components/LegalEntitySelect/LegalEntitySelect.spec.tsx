import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import * as useOffererNamesQueryModule from '@/commons/hooks/swr/useOffererNamesQuery'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { LegalEntitySelect } from './LegalEntitySelect'

vi.mock('@/commons/hooks/swr/useOffererNamesQuery')
vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
  },
}))

const renderLegalEntitySelect = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<LegalEntitySelect />, options)
}

describe('LegalEntitySelect', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.spyOn(
      useOffererNamesQueryModule,
      'useOffererNamesQuery'
    ).mockReturnValue({
      data: undefined,
      error: undefined,
      isLoading: false,
      isValidating: false,
      mutate: vi.fn(),
    })
  })

  it('should render select when there are multiple offerers', () => {
    const offerers = [
      getOffererNameFactory({ id: 1, name: 'Offerer A' }),
      getOffererNameFactory({ id: 2, name: 'Offerer B' }),
    ]
    const fullOfferer = {
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Offerer A',
    }

    renderLegalEntitySelect({
      storeOverrides: {
        offerer: {
          offererNames: offerers,
          adminCurrentOfferer: fullOfferer,
        },
      },
    })

    expect(screen.getByLabelText('Entité juridique')).toBeInTheDocument()
  })

  it('should display offerers sorted alphabetically by label', () => {
    const offerers = [
      getOffererNameFactory({ id: 1, name: 'Zebra Offerer' }),
      getOffererNameFactory({ id: 2, name: 'Alpha Offerer' }),
      getOffererNameFactory({ id: 3, name: 'Beta Offerer' }),
    ]
    const fullOfferer = {
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Zebra Offerer',
    }

    renderLegalEntitySelect({
      storeOverrides: {
        offerer: {
          offererNames: offerers,
          adminCurrentOfferer: fullOfferer,
        },
      },
    })

    const select = screen.getByLabelText('Entité juridique')
    const options = Array.from(
      select.querySelectorAll('option')
    ) as HTMLOptionElement[]

    expect(options[0].textContent).toBe('Alpha Offerer')
    expect(options[1].textContent).toBe('Beta Offerer')
    expect(options[2].textContent).toBe('Zebra Offerer')
  })

  it('should display the currently selected offerer', () => {
    const offerers = [
      getOffererNameFactory({ id: 1, name: 'Offerer A' }),
      getOffererNameFactory({ id: 2, name: 'Offerer B' }),
    ]
    const fullOfferer = {
      ...defaultGetOffererResponseModel,
      id: 2,
      name: 'Offerer B',
    }

    renderLegalEntitySelect({
      storeOverrides: {
        offerer: {
          offererNames: offerers,
          adminCurrentOfferer: fullOfferer,
        },
      },
    })

    const select = screen.getByLabelText(
      'Entité juridique'
    ) as HTMLSelectElement
    expect(select.value).toBe('2')
  })

  it('should dispatch setAdminCurrentOfferer when selection changes', async () => {
    const offerers = [
      getOffererNameFactory({ id: 1, name: 'Offerer A' }),
      getOffererNameFactory({ id: 2, name: 'Offerer B' }),
    ]
    const fullOfferer1 = {
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Offerer A',
    }
    const fullOfferer2 = {
      ...defaultGetOffererResponseModel,
      id: 2,
      name: 'Offerer B',
    }

    vi.mocked(api.getOfferer).mockResolvedValue(fullOfferer2)

    const { store } = renderLegalEntitySelect({
      storeOverrides: {
        offerer: {
          offererNames: offerers,
          adminCurrentOfferer: fullOfferer1,
        },
      },
    })

    const select = screen.getByLabelText('Entité juridique')
    await userEvent.selectOptions(select, '2')

    await waitFor(() => {
      const state = store.getState()
      expect(state.offerer.adminCurrentOfferer?.id).toBe(2)
      expect(api.getOfferer).toHaveBeenCalledWith(2)
    })
  })

  it('should not be disabled when not loading', () => {
    const offerers = [
      getOffererNameFactory({ id: 1, name: 'Offerer A' }),
      getOffererNameFactory({ id: 2, name: 'Offerer B' }),
    ]
    const fullOfferer = {
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Offerer A',
    }

    renderLegalEntitySelect({
      storeOverrides: {
        offerer: {
          offererNames: offerers,
          adminCurrentOfferer: fullOfferer,
        },
      },
    })

    const select = screen.getByLabelText('Entité juridique')
    expect(select).not.toBeDisabled()
  })
})
