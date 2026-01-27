import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'

import { ArtistSelect } from './ArtistSelect'

const label = 'Artistes'

describe('ArtistSelect', () => {
  it('should pass a11y tests', async () => {
    const { container } = render(<ArtistSelect label={label} name={label} />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should fetch artists on search', async () => {
    vi.spyOn(api, 'getArtists').mockResolvedValue([
      { id: 'abc', name: 'Dooz Kawa :(', thumbUrl: '' },
    ])

    render(<ArtistSelect label={label} name={label} />)

    await userEvent.type(screen.getByLabelText(label), 'Dooz Kawa')

    await userEvent.click(await screen.findByText('Dooz Kawa :('))
    expect(api.getArtists).toHaveBeenNthCalledWith(1, 'Dooz Kawa')
    expect(screen.getByLabelText(label)).toHaveValue('Dooz Kawa :(')
  })

  it('should not fetch artists on to short search', async () => {
    vi.spyOn(api, 'getArtists').mockResolvedValue([
      { id: 'abc', name: 'Dooz Kawa :(', thumbUrl: '' },
    ])

    render(<ArtistSelect label={label} name={label} />)

    await userEvent.type(screen.getByLabelText(label), 'U')

    expect(await screen.findByText('Aucun résultat')).toBeInTheDocument()
    expect(api.getArtists).not.toHaveBeenCalled()
  })

  it('should not fail when api fail', async () => {
    vi.spyOn(api, 'getArtists').mockRejectedValue([])

    render(<ArtistSelect label={label} name={label} />)
    await userEvent.type(screen.getByLabelText(label), 'Lucie Aubrac')
    expect(await screen.findByText('Aucun résultat')).toBeInTheDocument()
    await waitFor(() => {
      expect(api.getArtists).toHaveBeenCalled()
    })
  })

  it('should call onChange with the search text when typing', async () => {
    const onChangeSpy = vi.fn()
    render(<ArtistSelect label={label} name="artist" onChange={onChangeSpy} />)

    const input = screen.getByLabelText(label)

    await userEvent.type(input, 'Lucie')

    expect(onChangeSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        target: {
          name: 'artist',
          value: { artistId: '', name: 'Lucie' },
        },
      })
    )
  })
})
