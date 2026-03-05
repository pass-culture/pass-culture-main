import { useState } from 'react'
import { mutate } from 'swr'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import type { UploadImageValues } from '@/commons/utils/imageUploadTypes'
import type { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { postImageToVenue } from '@/repository/pcapi/pcapi'

import { buildInitialVenueImageValues } from '../utils/buildInitialVenueImageValues'

export const useOnVenueImageUpload = (venue: GetVenueResponseModel) => {
  const initialValues = buildInitialVenueImageValues(
    venue.bannerUrl,
    venue.bannerMeta
  )
  const venueId = venue.id

  const [imageValues, setImageValues] =
    useState<UploadImageValues>(initialValues)

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    const editedVenue = await postImageToVenue(
      venueId,
      imageFile,
      credit,
      cropParams?.x,
      cropParams?.y,
      cropParams?.height,
      cropParams?.width
    )
    setImageValues(
      buildInitialVenueImageValues(
        editedVenue.bannerUrl,
        editedVenue.bannerMeta
      )
    )

    await mutate([GET_VENUE_QUERY_KEY, String(venueId)])
  }

  return {
    imageValues,
    setImageValues,
    handleOnImageUpload,
  }
}
