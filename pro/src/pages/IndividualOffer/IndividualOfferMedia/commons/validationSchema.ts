import * as yup from 'yup'

import { isYoutubeValid } from './isYoutubeValid'
import { IndividualOfferMediaFormValues } from './types'

export const getValidationSchema = () => {
  return yup.object<IndividualOfferMediaFormValues>().shape({
    videoUrl: yup
      .string()
      .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
      .test({
        name: 'videoUrl',
        message:
          'Veuillez renseigner une URL provenant de la plateforme Youtube',
        test: (videoUrl?: string) => {
          if (!videoUrl) {
            return true
          }
          return isYoutubeValid(videoUrl)
        },
      })
      .nullable(),
  })
}
