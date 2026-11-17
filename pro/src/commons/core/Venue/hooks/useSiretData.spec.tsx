import { renderHook } from '@testing-library/react'
import { SWRConfig } from 'swr'

import { checkSiret, getSiretData } from '../utils/getSiretData'
import { useCheckSiret, useGetSiretData } from './useSiretData'

vi.mock('../utils/getSiretData', () => ({
  getSiretData: vi.fn(),
  checkSiret: vi.fn(),
}))

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <SWRConfig value={{ provider: () => new Map() }}>{children}</SWRConfig>
)

describe('useGetSiretData', () => {
  it('should return the siret data', async () => {
    const siretData = { siret: '12345678901234' }
    vi.mocked(getSiretData).mockResolvedValue(siretData as never)
    const { result } = renderHook(() => useGetSiretData(), { wrapper })

    await expect(result.current('123 456 789 01234')).resolves.toEqual(
      siretData
    )
    expect(getSiretData).toHaveBeenCalledWith('123 456 789 01234')
  })

  it('should reject on error and call the request again on the next trigger', async () => {
    vi.mocked(getSiretData)
      .mockRejectedValueOnce(new Error('SIRET trop court'))
      .mockResolvedValueOnce({ siret: '12345678901234' } as never)
    const { result } = renderHook(() => useGetSiretData(), { wrapper })

    await expect(result.current('1')).rejects.toThrow('SIRET trop court')
    await expect(result.current('1')).resolves.toEqual({
      siret: '12345678901234',
    })
    expect(getSiretData).toHaveBeenCalledTimes(2)
  })
})

describe('useCheckSiret', () => {
  it('should check the siret', async () => {
    vi.mocked(checkSiret).mockResolvedValue(undefined)
    const { result } = renderHook(() => useCheckSiret(), { wrapper })

    await result.current('12345678901234')

    expect(checkSiret).toHaveBeenCalledWith('12345678901234')
  })

  it('should reject when the check fails', async () => {
    vi.mocked(checkSiret).mockRejectedValue(new Error('SIRET vide'))
    const { result } = renderHook(() => useCheckSiret(), { wrapper })

    await expect(result.current('')).rejects.toThrow('SIRET vide')
  })
})
