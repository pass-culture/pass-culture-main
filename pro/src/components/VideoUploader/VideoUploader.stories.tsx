import type { StoryObj } from '@storybook/react'
import { Provider } from 'react-redux'
import { withRouter } from 'storybook-addon-remix-react-router'

import { configureTestStore } from '@/commons/store/testUtils'

import sampleImageLandscape from './assets/sample-image-landscape.jpg'
import { VideoUploader, type VideoUploaderProps } from './VideoUploader'

export default {
  title: '@/components/VideoUploader/VideoUploader',
  component: VideoUploader,
  decorators: [
    withRouter,
    (Story: any) => (
      <Provider store={configureTestStore({})}>
        <Story />
      </Provider>
    ),
  ],
}

const props: VideoUploaderProps = {}

export const WithImage: StoryObj<typeof VideoUploader> = {
  args: {
    ...props,
    videoImageUrl: sampleImageLandscape,
    videoTitle: 'Super titre de vidéo',
    videoDuration: 3,
  },
}

export const WithoutImage: StoryObj<typeof VideoUploader> = {
  args: {},
}
