import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { Target } from '@/apiClient/v1'
import { DEFAULT_ADDRESS_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import {
  resetSimulatorActivityAndTargetStorage,
  resetSimulatorSiretAndOpenToPublicStorage,
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
  saveActivityToStorage,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from './storage'

vi.mock('./storage', () => ({
  saveActivityToStorage: vi.fn(),
  saveOffererToStorage: vi.fn(),
  tryRestoreActivityFromStorage: vi.fn(),
  tryRestoreInitialAddressFromStorage: vi.fn(),
  tryRestoreOffererFromStorage: vi.fn(),
}))

vi.mock('@/pages/Simulator/storage', () => ({
  resetSimulatorActivityAndTargetStorage: vi.fn(),
  resetSimulatorSiretAndOpenToPublicStorage: vi.fn(),
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
  vi.clearAllMocks()
  // Nothing stored anywhere and no simulator data by default; each test
  // overrides what it actually needs.
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

describe('SignupJourneyContextProvider activity', () => {
  it('restores the activity from the signup journey storage when available, ignoring the simulator', () => {
    vi.mocked(tryRestoreActivityFromStorage).mockReturnValue({
      activity: 'STRUCTURE',
      targetCustomer: Target.EDUCATIONAL,
    } as never)

    renderProvider()

    expect(screen.getByTestId('activity')).toHaveTextContent('STRUCTURE')
    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.EDUCATIONAL
    )
    expect(tryRestoreSimulatorActivityFromStorage).not.toHaveBeenCalled()
  })

  it('falls back to the default values when nothing is stored and there is no simulator or URL data', () => {
    renderProvider()

    expect(screen.getByTestId('activity')).toHaveTextContent(
      DEFAULT_ACTIVITY_VALUES.activity ?? ''
    )
    expect(saveActivityToStorage).not.toHaveBeenCalled()
    expect(resetSimulatorActivityAndTargetStorage).not.toHaveBeenCalled()
  })

  it('falls back to the simulator activity and audiences when the signup journey storage is empty', () => {
    vi.mocked(tryRestoreSimulatorActivityFromStorage).mockReturnValue(
      'STRUCTURE' as never
    )
    vi.mocked(tryRestoreTargetAudienceFromStorage).mockReturnValue({
      individual: false,
      collective: true,
    } as never)

    renderProvider()

    expect(screen.getByTestId('activity')).toHaveTextContent('STRUCTURE')
    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.EDUCATIONAL
    )
    expect(saveActivityToStorage).toHaveBeenCalledTimes(1)
    expect(resetSimulatorActivityAndTargetStorage).toHaveBeenCalledTimes(1)
  })

  it('maps simulator audiences with both individual and collective to INDIVIDUAL_AND_EDUCATIONAL', () => {
    vi.mocked(tryRestoreTargetAudienceFromStorage).mockReturnValue({
      individual: true,
      collective: true,
    } as never)

    renderProvider()

    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.INDIVIDUAL_AND_EDUCATIONAL
    )
  })

  it('prioritizes the activity URL param over the simulator activity', () => {
    vi.mocked(tryRestoreSimulatorActivityFromStorage).mockReturnValue(
      'STRUCTURE' as never
    )

    renderProvider('?activity=COLLECTIVITE')

    expect(screen.getByTestId('activity')).toHaveTextContent('COLLECTIVITE')
  })

  it('prioritizes the targets URL param over the simulator audiences', () => {
    vi.mocked(tryRestoreTargetAudienceFromStorage).mockReturnValue({
      individual: false,
      collective: true,
    } as never)

    renderProvider('?targets=INDIVIDUAL')

    expect(screen.getByTestId('targetCustomer')).toHaveTextContent(
      Target.INDIVIDUAL
    )
  })
})

describe('SignupJourneyContextProvider offerer', () => {
  it('restores the offerer from the signup journey storage when available, ignoring the simulator', () => {
    vi.mocked(tryRestoreOffererFromStorage).mockReturnValue({
      siret: '11111111100011',
      isOpenToPublic: 'true',
    } as never)

    renderProvider()

    expect(screen.getByTestId('siret')).toHaveTextContent('11111111100011')
    expect(tryRestoreSiretFromStorage).not.toHaveBeenCalled()
  })

  it('falls back to the simulator siret and open-to-public value when nothing is stored', () => {
    vi.mocked(tryRestoreSiretFromStorage).mockReturnValue(
      '22222222200022' as never
    )
    vi.mocked(tryRestoreOpenToPublicFromStorage).mockReturnValue(
      'true' as never
    )

    renderProvider()

    expect(screen.getByTestId('siret')).toHaveTextContent('22222222200022')
    expect(screen.getByTestId('isOpenToPublic')).toHaveTextContent('true')
    expect(saveOffererToStorage).toHaveBeenCalledTimes(1)
    expect(resetSimulatorSiretAndOpenToPublicStorage).toHaveBeenCalledTimes(1)
  })

  it('prioritizes the siret and isOpenToPublic URL params over the simulator storage', () => {
    vi.mocked(tryRestoreSiretFromStorage).mockReturnValue(
      '22222222200022' as never
    )
    vi.mocked(tryRestoreOpenToPublicFromStorage).mockReturnValue(
      'true' as never
    )

    renderProvider('?siret=33333333300033&isOpenToPublic=false')

    expect(screen.getByTestId('siret')).toHaveTextContent('33333333300033')
    expect(screen.getByTestId('isOpenToPublic')).toHaveTextContent('false')
  })

  it('does not persist or reset the simulator storage when there is nothing new to merge', () => {
    renderProvider()

    expect(saveOffererToStorage).not.toHaveBeenCalled()
    expect(resetSimulatorSiretAndOpenToPublicStorage).not.toHaveBeenCalled()
  })
})

describe('SignupJourneyContextProvider initial address', () => {
  it('restores the initial address from storage when available', () => {
    const storedAddress = { city: 'Paris' }
    vi.mocked(tryRestoreInitialAddressFromStorage).mockReturnValue(
      storedAddress as never
    )

    renderProvider()

    expect(screen.getByTestId('initialAddress')).toHaveTextContent(
      JSON.stringify(storedAddress)
    )
  })

  it('falls back to the default address when nothing is stored', () => {
    renderProvider()

    expect(screen.getByTestId('initialAddress')).toHaveTextContent(
      JSON.stringify(DEFAULT_ADDRESS_FORM_VALUES)
    )
  })
})
