// This file will be replace by apiClient
/* istanbul ignore file */

import {
  AttachImageResponseModel,
  CreateThumbnailResponseModel,
} from 'apiClient/v1'
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

//
// thumbnail
//

type LegacyPostImageMethodType<T> = (
  offerId: string,
  thumb: File,
  credit: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => Promise<T>

export const legacyPostImage = (
  url: string,
  offerId: string,
  thumb: File,
  credit?: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => {
  const body = new FormData()
  body.append('offerId', offerId)
  body.append('thumb', thumb)
  body.append('credit', credit ?? '')
  body.append('croppingRectX', x !== undefined ? String(x) : '')
  body.append('croppingRectY', y !== undefined ? String(y) : '')
  body.append('croppingRectHeight', height !== undefined ? String(height) : '')
  body.append('croppingRectWidth', width !== undefined ? String(width) : '')
  body.append('thumbUrl', thumbUrl ?? '')

  return client.postWithFormData(url, body)
}

type PostImageMethodType<T> = (
  offerId: number,
  thumb: File,
  credit: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => Promise<T>

export const postImage = (
  url: string,
  offerId: number,
  thumb: File,
  credit?: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => {
  const body = new FormData()
  body.append('offerId', offerId.toString())
  body.append('thumb', thumb)
  body.append('credit', credit ?? '')
  body.append('croppingRectX', x !== undefined ? String(x) : '')
  body.append('croppingRectY', y !== undefined ? String(y) : '')
  body.append('croppingRectHeight', height !== undefined ? String(height) : '')
  body.append('croppingRectWidth', width !== undefined ? String(width) : '')
  body.append('thumbUrl', thumbUrl ?? '')

  return client.postWithFormData(url, body)
}

export const postThumbnail: LegacyPostImageMethodType<
  CreateThumbnailResponseModel
> = (...args) => legacyPostImage('/offers/thumbnails', ...args)

export const postCollectiveOfferImage: PostImageMethodType<
  AttachImageResponseModel
> = (offerId, ...args) =>
  postImage(`/collective/offers/${offerId}/image`, offerId, ...args)

export const postCollectiveOfferTemplateImage: PostImageMethodType<
  AttachImageResponseModel
> = (offerId, ...args) =>
  postImage(`/collective/offers-template/${offerId}/image`, offerId, ...args)
