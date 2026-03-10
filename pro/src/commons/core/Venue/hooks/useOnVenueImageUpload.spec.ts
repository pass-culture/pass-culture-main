import { act, renderHook } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { mutate } from 'swr'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { configureTestStore } from '@/commons/store/testUtils'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { postImageToVenue } from '@/repository/pcapi/pcapi'

import { buildInitialVenueImageValues } from '../utils/buildInitialVenueImageValues'
import { useOnVenueImageUpload } from './useOnVenueImageUpload'

vi.mock('swr', () => ({ mutate: vi.fn() }))
vi.mock('@/repository/pcapi/pcapi', () => ({ postImageToVenue: vi.fn() }))
vi.mock('../utils/buildInitialVenueImageValues', () => ({
  buildInitialVenueImageValues: vi.fn(),
}))

const venue = makeGetVenueResponseModel({
  id: 42,
  managingOffererId: 3,
  name: 'Club Dorothy',
  bannerUrl: 'https://example.com/banner.jpg',
  bannerMeta: {
    alt_text: 'banner',
    author: 'author',
    image_credit: 'credit',
    crop_params: {
      height_crop_percent: 12,
      width_crop_percent: 12,
      x_crop_percent: 12,
      y_crop_percent: 12,
    },
  },
})

const mockInitialValues = {
  url: 'https://example.com/banner.jpg',
  credit: 'credit',
}

const mockUpdatedValues = {
  url: 'https://example.com/new-banner.jpg',
  credit: 'new-credit',
}
const mockEditedVenue = {
  bannerUrl: 'https://example.com/new-banner.jpg',
  bannerMeta: { alt_text: 'new', author: 'new', image_credit: 'new-credit' },
}

const renderUseOnVenueImageUpload = () => {
  const store = configureTestStore()
  const wrapper: React.FC<{ children?: React.ReactNode }> = ({ children }) =>
    React.createElement(Provider, { store, children })

  return renderHook(
    () => useOnVenueImageUpload(venue.id, venue.bannerUrl, venue.bannerMeta),
    {
      wrapper,
    }
  )
}

describe('useOnVenueImageUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(buildInitialVenueImageValues).mockReturnValue(mockInitialValues)
  })

  it('should initialize image values with venue data', () => {
    const { result } = renderUseOnVenueImageUpload()
    expect(buildInitialVenueImageValues).toHaveBeenCalledWith(
      venue.bannerUrl,
      venue.bannerMeta
    )
    expect(result.current.imageValues).toEqual(mockInitialValues)
  })

  it('should update image values and call mutate after upload', async () => {
    vi.mocked(postImageToVenue).mockResolvedValue(mockEditedVenue)
    vi.mocked(buildInitialVenueImageValues)
      .mockReturnValueOnce(mockInitialValues) // initial call
      .mockReturnValueOnce(mockUpdatedValues) // call after upload

    const { result } = renderUseOnVenueImageUpload()

    const uploadArgs = {
      imageFile: new File(['img'], 'photo.jpg', { type: 'image/jpeg' }),
      credit: 'new-credit',
      cropParams: { x: 10, y: 20, height: 100, width: 200 },
    }

    await act(async () => {
      await result.current.handleOnImageUpload(uploadArgs)
    })

    expect(postImageToVenue).toHaveBeenCalledWith(
      venue.id,
      uploadArgs.imageFile,
      uploadArgs.credit,
      uploadArgs.cropParams.x,
      uploadArgs.cropParams.y,
      uploadArgs.cropParams.height,
      uploadArgs.cropParams.width
    )

    expect(buildInitialVenueImageValues).toHaveBeenCalledWith(
      mockEditedVenue.bannerUrl,
      mockEditedVenue.bannerMeta
    )
    expect(result.current.imageValues).toEqual(mockUpdatedValues)
    expect(mutate).toHaveBeenCalledWith([GET_VENUE_QUERY_KEY, String(venue.id)])
  })
})
