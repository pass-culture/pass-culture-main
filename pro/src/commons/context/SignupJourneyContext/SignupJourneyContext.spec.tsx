import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { Target } from '@/apiClient/v1'
import { DEFAULT_ADDRESS_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import {
  resetSimulatorStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreActivityFromStorage as tryRestoreSimulatorActivityFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from '@/pages/Simulator/storage'

import { DEFAULT_ACTIVITY_VALUES } from './constants'
import {
  SignupJourneyContextProvider,
  useSignupJourneyContext,
} from './SignupJourneyContext'
import {
  cleanInitialAddressStorage,
  saveActivityToStorage,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from './storage'

vi.mock('./storage', () => ({
  saveActivityToStorage: vi.fn(),
  saveOffererToStorage: vi.fn(),
  cleanInitialAddressStorage: vi.fn(),
  tryRestoreActivityFromStorage: vi.fn(),
  tryRestoreInitialAddressFromStorage: vi.fn(),
  tryRestoreOffererFromStorage: vi.fn(),
}))

vi.mock('@/pages/Simulator/storage', () => ({
  resetSimulatorStorage: vi.fn(),
  tryRestoreOpenToPublicFromStorage: vi.fn(),
  tryRestoreActivityFromStorage: vi.fn(),
  tryRestoreSiretFromStorage: vi.fn(),
  tryRestoreTargetAudienceFromStorage: vi.fn(),
}))

const throwNotFound = () => {
  throw new Error('nothing stored')
}

const TestConsumer = () => {
  const { activity, offerer, initialAddress } = useSignupJourneyContext()

  return (
    <div>
      <span data-testid="activity">{activity?.activity}</span>
      <span data-testid="targetCustomer">{activity?.targetCustomer}</span>
      <span data-testid="siret">{offerer?.siret}</span>
      <span data-testid="isOpenToPublic">
        {String(offerer?.isOpenToPublic)}
      </span>
      <span data-testid="initialAddress">{JSON.stringify(initialAddress)}</span>
    </div>
  )
}

const renderProvider = (search = '') =>
  render(
    <MemoryRouter initialEntries={[`/inscription${search}`]}>
      <SignupJourneyContextProvider>
        <TestConsumer />
      </SignupJourneyContextProvider>
    </MemoryRouter>
  )

beforeEach(() => {
  vi.mocked(tryRestoreActivityFromStorage).mockImplementation(throwNotFound)
  vi.mocked(tryRestoreOffererFromStorage).mockImplementation(throwNotFound)
  vi.mocked(tryRestoreInitialAddressFromStorage).mockImplementation(
    throwNotFound
  )
  vi.mocked(tryRestoreSimulatorActivityFromStorage).mockReturnValue(
    null as never
  )
  vi.mocked(tryRestoreTargetAudienceFromStorage).mockReturnValue(null as never)
  vi.mocked(tryRestoreSiretFromStorage).mockReturnValue(null as never)
  vi.mocked(tryRestoreOpenToPublicFromStorage).mockReturnValue(null as never)
})

describe('SignupJourneyContextProvider - Scenario 1: Simulator Migration (SIRET is present)', () => {
  it('loads data from simulator, saves it to standard storage, and clears simulator storage', () => {
    vi.mocked(tryRestoreSiretFromStorage).mockReturnValue(
      '22222222200022' as never
    )
    vi.mocked(tryRestoreSimulatorActivityFromStorage).mockReturnValue(
      'STRUCTURE' as never
    )
    vi.mocked(tryRestoreOpenToPublicFromStorage).mockReturnValue(
      'true' as never
    )
    vi.mocked(tryRestoreTargetAudienceFromStorage).mockReturnValue({
      individual: false,
      collective: true,
    } as never)

    renderProvider()

    expect(screen.getByTestId('siret')).toHaveTextContent('22222222200022')
    expect(screen.getByTestId('activity')).toHaveTextContent('STRUCTURE')
    expect(screen.getByTestId('isOpenToPublic')).toHaveTextContent('true')
    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.EDUCATIONAL
    )
    expect(screen.getByTestId('initialAddress')).toHaveTextContent(
      JSON.stringify(DEFAULT_ADDRESS_FORM_VALUES)
    )

    expect(saveActivityToStorage).toHaveBeenCalledTimes(1)
    expect(saveOffererToStorage).toHaveBeenCalledTimes(1)
    expect(cleanInitialAddressStorage).toHaveBeenCalledTimes(1)
    expect(resetSimulatorStorage).toHaveBeenCalledTimes(1)
  })

  it('prioritizes URL parameters over simulator storage values', () => {
    vi.mocked(tryRestoreSiretFromStorage).mockReturnValue(
      '22222222200022' as never
    )
    vi.mocked(tryRestoreSimulatorActivityFromStorage).mockReturnValue(
      'STRUCTURE' as never
    )
    vi.mocked(tryRestoreOpenToPublicFromStorage).mockReturnValue(
      'true' as never
    )

    renderProvider(
      '?siret=33333333300033&activity=COLLECTIVITE&isOpenToPublic=false&targets=INDIVIDUAL'
    )

    expect(screen.getByTestId('siret')).toHaveTextContent('33333333300033')
    expect(screen.getByTestId('activity')).toHaveTextContent('COLLECTIVITE')
    expect(screen.getByTestId('isOpenToPublic')).toHaveTextContent('false')
    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.INDIVIDUAL
    )

    expect(saveActivityToStorage).toHaveBeenCalledTimes(1)
    expect(saveOffererToStorage).toHaveBeenCalledTimes(1)
    expect(cleanInitialAddressStorage).toHaveBeenCalledTimes(1)
    expect(resetSimulatorStorage).toHaveBeenCalledTimes(1)
  })

  it('maps simulator audiences with both individual and collective to INDIVIDUAL_AND_EDUCATIONAL', () => {
    vi.mocked(tryRestoreSiretFromStorage).mockReturnValue(
      '22222222200022' as never
    )
    vi.mocked(tryRestoreTargetAudienceFromStorage).mockReturnValue({
      individual: true,
      collective: true,
    } as never)

    renderProvider()

    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.INDIVIDUAL_AND_EDUCATIONAL
    )
  })
})

describe('SignupJourneyContextProvider - Scenario 2: Standard Storage Restoration', () => {
  it('restores all contexts from the signup journey storage when no SIRET is in simulator or URL', () => {
    vi.mocked(tryRestoreActivityFromStorage).mockReturnValue({
      activity: 'STRUCTURE',
      targetCustomer: Target.EDUCATIONAL,
    } as never)
    vi.mocked(tryRestoreOffererFromStorage).mockReturnValue({
      siret: '11111111100011',
      isOpenToPublic: 'true',
    } as never)
    const storedAddress = { city: 'Paris' }
    vi.mocked(tryRestoreInitialAddressFromStorage).mockReturnValue(
      storedAddress as never
    )

    renderProvider()

    expect(screen.getByTestId('activity')).toHaveTextContent('STRUCTURE')
    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.EDUCATIONAL
    )
    expect(screen.getByTestId('siret')).toHaveTextContent('11111111100011')
    expect(screen.getByTestId('isOpenToPublic')).toHaveTextContent('true')
    expect(screen.getByTestId('initialAddress')).toHaveTextContent(
      JSON.stringify(storedAddress)
    )

    expect(saveActivityToStorage).not.toHaveBeenCalled()
    expect(saveOffererToStorage).not.toHaveBeenCalled()
    expect(cleanInitialAddressStorage).not.toHaveBeenCalled()
    expect(resetSimulatorStorage).not.toHaveBeenCalled()
  })
})

describe('SignupJourneyContextProvider - Scenario 3: Complete Fallback', () => {
  it('falls back to the absolute default values when nothing is stored and there is no URL data', () => {
    renderProvider()

    expect(screen.getByTestId('activity')).toHaveTextContent(
      DEFAULT_ACTIVITY_VALUES.activity ?? ''
    )
    expect(screen.getByTestId('siret')).toHaveTextContent('')
    expect(screen.getByTestId('initialAddress')).toHaveTextContent(
      JSON.stringify(DEFAULT_ADDRESS_FORM_VALUES)
    )

    expect(saveActivityToStorage).not.toHaveBeenCalled()
    expect(saveOffererToStorage).not.toHaveBeenCalled()
    expect(cleanInitialAddressStorage).not.toHaveBeenCalled()
    expect(resetSimulatorStorage).not.toHaveBeenCalled()
  })
})
