// This file will be replace by apiClient
/* istanbul ignore file */

import { client } from 'repository/pcapi/pcapiClient'
import { stringify } from 'utils/query-string'

//
// venues
//

export const postImageToVenue = async (
  venueId: number,
  banner: File,
  imageCredit: string | null,
  xCropPercent?: number,
  yCropPercent?: number,
  heightCropPercent?: number,
  widthCropPercent?: number
) => {
  const body = new FormData()
  body.append('banner', banner)

  const venueImage = {
    x_crop_percent: xCropPercent,
    y_crop_percent: yCropPercent,
    height_crop_percent: heightCropPercent,
    width_crop_percent: widthCropPercent,
  }

  if (imageCredit) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'image_credit' does not exist on type '{ ... Remove this comment to see the full error message
    venueImage.image_credit = imageCredit
  }

  // @ts-expect-error
  const queryParams = stringify(venueImage)

  return await client.postWithFormData(
    `/venues/${venueId}/banner?${queryParams}`,
    body
  )
}
