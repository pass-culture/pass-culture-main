import '@testing-library/jest-dom'

import { renderHook } from '@testing-library/react-hooks'

import useParticipantUpdates from '../useParticipantUpdates'

describe('useParticipantUpdates', () => {
  it('should set all participants to true when user selects "all"', async () => {
    const handleChange = jest.fn()
    let value = {
      quatrieme: false,
      troisieme: false,
      seconde: false,
      premiere: false,
      terminale: false,
      CAPAnnee1: false,
      CAPAnnee2: false,
      all: false,
    }
    const { rerender } = renderHook(() =>
      useParticipantUpdates(value, handleChange)
    )
    value = {
      quatrieme: false,
      troisieme: false,
      seconde: false,
      premiere: false,
      terminale: false,
      CAPAnnee1: false,
      CAPAnnee2: false,
      all: true,
    }

    rerender()

    expect(handleChange).toHaveBeenCalledWith({
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: true,
    })
  })

  it('should set all participants to false when user unselects "all"', async () => {
    const handleChange = jest.fn()
    let value = {
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: true,
    }
    const { rerender } = renderHook(() =>
      useParticipantUpdates(value, handleChange)
    )
    value = {
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: false,
    }

    rerender()

    expect(handleChange).toHaveBeenCalledWith({
      quatrieme: false,
      troisieme: false,
      seconde: false,
      premiere: false,
      terminale: false,
      CAPAnnee1: false,
      CAPAnnee2: false,
      all: false,
    })
  })

  it('should select "all" when user selects all participants', async () => {
    const handleChange = jest.fn()
    let value = {
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: false,
      all: false,
    }
    const { rerender } = renderHook(() =>
      useParticipantUpdates(value, handleChange)
    )
    value = {
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: false,
    }

    rerender()

    expect(handleChange).toHaveBeenCalledWith({
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: true,
    })
  })

  it('should unselect "all" when user deselects one participant', async () => {
    const handleChange = jest.fn()
    let value = {
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: true,
    }
    const { rerender } = renderHook(() =>
      useParticipantUpdates(value, handleChange)
    )
    value = {
      quatrieme: false,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: true,
    }

    rerender()

    expect(handleChange).toHaveBeenCalledWith({
      quatrieme: false,
      troisieme: true,
      seconde: true,
      premiere: true,
      terminale: true,
      CAPAnnee1: true,
      CAPAnnee2: true,
      all: false,
    })
  })

  it('should not change "all"', async () => {
    const handleChange = jest.fn()
    let value = {
      quatrieme: true,
      troisieme: true,
      seconde: false,
      premiere: false,
      terminale: false,
      CAPAnnee1: false,
      CAPAnnee2: false,
      all: false,
    }
    const { rerender } = renderHook(() =>
      useParticipantUpdates(value, handleChange)
    )
    value = {
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: false,
      terminale: false,
      CAPAnnee1: false,
      CAPAnnee2: false,
      all: true,
    }

    rerender()

    expect(handleChange).toHaveBeenCalledWith({
      quatrieme: true,
      troisieme: true,
      seconde: true,
      premiere: false,
      terminale: false,
      CAPAnnee1: false,
      CAPAnnee2: false,
      all: true,
    })
  })
})
