import { render, screen } from '@testing-library/react'
import { forwardRef } from 'react'
import { FormProvider, type UseFormGetValues, useForm } from 'react-hook-form'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import { type ArtistOfferLinkResponseModel, ArtistType } from '@/apiClient/v1'

import { ArtistField } from './ArtistField'

vi.mock('@/apiClient/api', () => ({
  api: { getArtists: vi.fn() },
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

  it('onSearch should update form value with search text', () => {
    const { getValues } = renderArtistField()
    const props = apiSelectSpy.mock.calls[0][0]

    props.onSearch?.('John')

    const artistOfferLinks = getValues().artistOfferLinks
    const authorLink = artistOfferLinks[0]
    expect(authorLink).toEqual({
      artistId: null,
      artistName: 'John',
      artistType: ArtistType.AUTHOR,
    })
  })

  it('onSelect should update form value with selected artist object', () => {
    const { getValues } = renderArtistField()
    const props = apiSelectSpy.mock.calls[0][0]

    props.onSelect({
      id: '42',
      name: 'John Doe',
    })

    const artistOfferLinks = getValues().artistOfferLinks
    const authorLink = artistOfferLinks[0]
    expect(authorLink).toEqual({
      artistId: '42',
      artistName: 'John Doe',
      artistType: ArtistType.AUTHOR,
    })
  })
})
