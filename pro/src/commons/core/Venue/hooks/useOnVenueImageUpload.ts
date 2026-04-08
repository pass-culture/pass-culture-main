import { useState } from 'react'

import type { BannerMetaModel } from '@/apiClient/v1'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import type { UploadImageValues } from '@/commons/utils/imageUploadTypes'
import type { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { postImageToVenue } from '@/repository/pcapi/pcapi'

import { buildInitialVenueImageValues } from '../utils/buildInitialVenueImageValues'

export const useOnVenueImageUpload = (
  venueId: number,
  venueBannerUrl?: string | null,
  venueBannerMeta?: BannerMetaModel | null
) => {
  const { syncVenueWithData } = useSyncVenueCache()
  const initialValues = buildInitialVenueImageValues(
    venueBannerUrl,
    venueBannerMeta
  )

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

    await syncVenueWithData(venueId, editedVenue)
  }

  return {
    imageValues,
    setImageValues,
    handleOnImageUpload,
  }
}
