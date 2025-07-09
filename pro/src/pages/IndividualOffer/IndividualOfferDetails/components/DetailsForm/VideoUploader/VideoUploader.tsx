import { useFormContext } from 'react-hook-form'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from '../DetailsForm.module.scss'

import { VideoUploaderTips } from './VideoUploaderTips/VideoUploaderTips'

export const VideoUploader = () => {
  const {
    register,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  return (
    <FormLayout.Section title="Ajoutez une vidéo">
      <FormLayout.Row
        className={styles['row']}
        sideComponent={<VideoUploaderTips />}
      >
        <TextInput
          label="Lien URL Youtube"
          type="text"
          description="Format : https://www.youtube.com/watch?v=0R5PZxOgoz8"
          {...register('videoUrl')}
          error={errors.videoUrl?.message}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
