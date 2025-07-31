import * as yup from 'yup'

import { IndividualOfferMediaFormValues } from './types'

// This regex is a replicate of what exists backend-side.
// Mind that frontend / backend controls regarding video url always match.
const youtubeVideoRegex = new RegExp(
  /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})/
)

export const getValidationSchema = () => {
  return yup.object<IndividualOfferMediaFormValues>().shape({
    videoUrl: yup
      .string()
      .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
      .test({
        name: 'videoUrl',
        message:
          'Veuillez renseigner une URL provenant de la plateforme Youtube',
        test: (videoUrl?: string) =>
          videoUrl ? youtubeVideoRegex.exec(videoUrl) !== null : true,
      })
      .nullable(),
  })
}
