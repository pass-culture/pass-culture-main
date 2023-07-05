import { renderHook } from '@testing-library/react'
import * as router from 'react-router-dom'

import useActiveStep from 'hooks/useActiveStep'

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useLocation: () => ({
    pathname: '',
  }),
}))

describe('useActiveStep', () => {
  it('should return empty string if location is wrong', async () => {
    vi.spyOn(router, 'useLocation').mockReturnValue({
      pathname: '',
      search: '',
      hash: '',
      state: null,
      key: 's',
    })
    const { result } = renderHook(() => useActiveStep())
    expect(result.current).toEqual('')
  })

  it('should return last part of url path', async () => {
    vi.spyOn(router, 'useLocation').mockReturnValue({
      pathname: '/offre/individuelle/creation/informations',
      search: '',
      hash: '',
      state: null,
      key: 's',
    })
    const { result } = renderHook(() => useActiveStep())
    expect(result.current).toEqual('informations')
  })

  it('should return first allowed step if requested step is not allowed', async () => {
    vi.spyOn(router, 'useLocation').mockReturnValue({
      pathname: '/offre/individuelle/creation/stocks',
      search: '',
      hash: '',
      state: null,
      key: 's',
    })
    const { result } = renderHook(() => useActiveStep(['informations']))
    expect(result.current).toEqual('informations')
  })
})
