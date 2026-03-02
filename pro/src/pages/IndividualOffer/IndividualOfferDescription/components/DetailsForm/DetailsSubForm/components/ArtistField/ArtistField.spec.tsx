import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { forwardRef } from 'react'
import { FormProvider, type UseFormGetValues, useForm } from 'react-hook-form'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import { type ArtistOfferLinkResponseModel, ArtistType } from '@/apiClient/v1'
import { resizeImageURL } from '@/commons/utils/resizeImageURL'

import { ArtistField } from './ArtistField'

vi.mock('@/apiClient/api', () => ({
  api: { getArtists: vi.fn() },
}))

vi.mock('@/commons/utils/resizeImageURL', () => ({
  resizeImageURL: vi.fn((args) => `resized-${args.imageURL}`),
}))

const apiSelectSpy = vi.fn()

vi.mock('@/ui-kit/form/ApiSelect/ApiSelect', () => ({
  ApiSelect: forwardRef((props, _ref) => {
    apiSelectSpy(props)
    return <span data-testid="mock-api-select" />
  }),
}))

const renderArtistField = ({
  artistType = ArtistType.AUTHOR,
  readOnly = false,
  defaultArtistOfferLinks = [
    {
      artistId: 'any-id',
      artistName: 'any-name',
      artistType: ArtistType.AUTHOR,
    },
  ],
}: {
  artistType?: ArtistType
  readOnly?: boolean
  defaultArtistOfferLinks?: ArtistOfferLinkResponseModel[]
} = {}) => {
  let getValues: UseFormGetValues<{
    artistOfferLinks: ArtistOfferLinkResponseModel[]
  }>

  const Wrapper = () => {
    const form = useForm({
      defaultValues: { artistOfferLinks: defaultArtistOfferLinks },
    })
    getValues = form.getValues
    return (
      <FormProvider {...form}>
        <ArtistField artistType={artistType} readOnly={readOnly} />
      </FormProvider>
    )
  }
  return {
    ...render(<Wrapper />),
    getValues: () => getValues(),
  }
}

describe('ArtistField', () => {
  beforeEach(() => {
    apiSelectSpy.mockClear()
    vi.mocked(api.getArtists).mockResolvedValue([
      { id: '1', name: 'Alice', thumbUrl: 'any-url' },
      { id: '2', name: 'Bob', thumbUrl: 'any-url' },
    ])
  })

  it('should pass label "Auteur" to ApiSelect', () => {
    renderArtistField()

    const props = apiSelectSpy.mock.calls[0][0]

    expect(screen.queryByTestId('mock-api-select')).toBeInTheDocument()
    expect(props.label).toBe('Auteur')
    expect(props.name).toBe('artistOfferLinks.0')
    expect(props.minSearchLength).toBe(2)
    expect(props.disabled).toBe(false)
    expect(props.required).toBe(false)
    expect(props.thumbPlaceholder).toBeDefined()
  })

  it('should not render ApiSelect', () => {
    renderArtistField({ artistType: ArtistType.PERFORMER })
    expect(screen.queryByTestId('mock-api-select')).not.toBeInTheDocument()
  })

  it('should pass label "Interprète" to ApiSelect', () => {
    const performerLink = [
      {
        artistId: 'any-id',
        artistName: 'any-name',
        artistType: ArtistType.PERFORMER,
      },
    ]
    renderArtistField({
      artistType: ArtistType.PERFORMER,
      defaultArtistOfferLinks: performerLink,
    })
    expect(apiSelectSpy).toHaveBeenCalledWith(
      expect.objectContaining({ label: 'Interprète' })
    )
  })

  it('should pass label "Metteur en scène" to ApiSelect', () => {
    const stageDirectorLink = [
      {
        artistId: 'any-id',
        artistName: 'any-name',
        artistType: ArtistType.STAGE_DIRECTOR,
      },
    ]
    renderArtistField({
      artistType: ArtistType.STAGE_DIRECTOR,
      defaultArtistOfferLinks: stageDirectorLink,
    })
    expect(apiSelectSpy).toHaveBeenCalledWith(
      expect.objectContaining({ label: 'Metteur en scène' })
    )
  })

  it('should disable ApiSelect', () => {
    renderArtistField({ readOnly: true })
    const props = apiSelectSpy.mock.calls[0][0]
    expect(props.disabled).toBe(true)
  })

  it('searchApi should call api.getArtists and map results', async () => {
    renderArtistField()
    const props = apiSelectSpy.mock.calls[0][0]

    const result = await props.searchApi('Al')
    expect(api.getArtists).toHaveBeenCalledWith('Al')
    expect(result).toEqual([
      expect.objectContaining({ value: '1', label: 'Alice' }),
      expect.objectContaining({ value: '2', label: 'Bob' }),
    ])
  })

  it('searchApi should call image resize function for artist thumbnails', async () => {
    renderArtistField()
    const props = apiSelectSpy.mock.calls[0][0]

    await props.searchApi('Al')

    expect(resizeImageURL).toHaveBeenCalledTimes(2)
    expect(resizeImageURL).toHaveBeenCalledWith({
      imageURL: 'any-url',
      width: 36,
    })
  })

  it('onSearch should update form value with search text', async () => {
    const { getValues } = renderArtistField()
    const props = apiSelectSpy.mock.calls[0][0]

    props.onSearch?.('John')

    await waitFor(() => {
      const artistOfferLinks = getValues().artistOfferLinks
      expect(artistOfferLinks[0]).toEqual({
        artistId: null,
        artistName: 'John',
        artistType: ArtistType.AUTHOR,
      })
    })
  })

  it('onSelect should update form value with selected artist object', async () => {
    const { getValues } = renderArtistField()
    const props = apiSelectSpy.mock.calls[0][0]

    props.onSelect({ id: '42', name: 'John Doe' })

    await waitFor(() => {
      const artistOfferLinks = getValues().artistOfferLinks
      expect(artistOfferLinks[0]).toEqual({
        artistId: '42',
        artistName: 'John Doe',
        artistType: ArtistType.AUTHOR,
      })
    })
  })

  it('should render button to add artist', () => {
    renderArtistField({ readOnly: false })

    expect(
      screen.getByRole('button', { name: /Ajouter un auteur/i })
    ).toBeInTheDocument()
  })

  it('should not render button to add artist when readOnly', () => {
    renderArtistField({ readOnly: true })

    expect(
      screen.queryByRole('button', { name: /Ajouter un auteur/i })
    ).not.toBeInTheDocument()
  })

  it('should add new artist field when clicking add button', async () => {
    const { getValues } = renderArtistField({ readOnly: false })

    const addButton = screen.getByRole('button', { name: /Ajouter un auteur/i })
    await userEvent.click(addButton)

    const artistOfferLinks = getValues().artistOfferLinks
    expect(artistOfferLinks).toHaveLength(2)
    expect(artistOfferLinks[1]).toEqual({
      artistId: null,
      artistName: '',
      artistType: ArtistType.AUTHOR,
    })
  })

  it('should reset artist field when trashing the only existing artist link', async () => {
    const { getValues } = renderArtistField({
      defaultArtistOfferLinks: [
        {
          artistId: '42',
          artistName: 'John Doe',
          artistType: ArtistType.AUTHOR,
        },
      ],
    })

    const trashButton = screen.getByRole('button', {
      name: /Réinitialiser les valeurs de ce champ/i,
    })
    await userEvent.click(trashButton)

    const artistOfferLinks = getValues().artistOfferLinks
    expect(artistOfferLinks).toHaveLength(1)
    expect(artistOfferLinks[0]).toEqual({
      artistId: null,
      artistName: '',
      artistType: ArtistType.AUTHOR,
    })
  })

  it('should disable trash button when there is only one artist field and it is empty', () => {
    renderArtistField({
      defaultArtistOfferLinks: [
        {
          artistId: null,
          artistName: '',
          artistType: ArtistType.AUTHOR,
        },
      ],
    })

    const trashButton = screen.getByRole('button', {
      name: /Réinitialiser les valeurs de ce champ/i,
    })
    expect(trashButton).toBeDisabled()
  })

  it('should disable trash button when there is only one artist of current type and it is empty, even if other types exist', () => {
    renderArtistField({
      artistType: ArtistType.AUTHOR,
      defaultArtistOfferLinks: [
        {
          artistId: null,
          artistName: '',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: '2',
          artistName: 'Performer 1',
          artistType: ArtistType.PERFORMER,
        },
      ],
    })

    const trashButton = screen.getByRole('button', {
      name: /Réinitialiser les valeurs de ce champ/i,
    })
    expect(trashButton).toBeDisabled()
  })

  it('should remove artist field when trashing one of multiple artist links', async () => {
    const { getValues } = renderArtistField({
      defaultArtistOfferLinks: [
        {
          artistId: '1',
          artistName: 'Author 1',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: '2',
          artistName: 'Author 2',
          artistType: ArtistType.AUTHOR,
        },
      ],
    })

    const trashButtons = screen.getAllByRole('button', {
      name: /Supprimer ce champ/i,
    })
    await userEvent.click(trashButtons[0])

    const artistOfferLinks = getValues().artistOfferLinks
    expect(artistOfferLinks).toHaveLength(1)
    expect(artistOfferLinks[0].artistName).toBe('Author 2')
  })

  it('should reset artist field when trashing an artist while another type exists but it is the only one of its type', async () => {
    const { getValues } = renderArtistField({
      artistType: ArtistType.AUTHOR,
      defaultArtistOfferLinks: [
        {
          artistId: '1',
          artistName: 'Author 1',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: '2',
          artistName: 'Performer 1',
          artistType: ArtistType.PERFORMER,
        },
      ],
    })

    const trashButton = screen.getByRole('button', {
      name: /Réinitialiser les valeurs de ce champ/i,
    })
    await userEvent.click(trashButton)

    const artistOfferLinks = getValues().artistOfferLinks
    expect(artistOfferLinks).toHaveLength(2)
    expect(artistOfferLinks[0]).toEqual({
      artistId: null,
      artistName: '',
      artistType: ArtistType.AUTHOR,
    })
    expect(artistOfferLinks[1].artistType).toBe(ArtistType.PERFORMER)
  })

  it('should not show trash button when readOnly is true', () => {
    renderArtistField({
      readOnly: true,
      defaultArtistOfferLinks: [
        {
          artistId: '1',
          artistName: 'Author 1',
          artistType: ArtistType.AUTHOR,
        },
      ],
    })

    expect(
      screen.queryByRole('button', {
        name: /Réinitialiser les valeurs de ce champ/i,
      })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Supprimer ce champ/i })
    ).not.toBeInTheDocument()
  })
})
