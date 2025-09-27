import type { StoryObj } from '@storybook/react-vite'
import { Provider } from 'react-redux'
import { withRouter } from 'storybook-addon-remix-react-router'

import { configureTestStore } from '@/commons/store/testUtils'

import sampleImageLandscape from './assets/sample-image-landscape.jpg'
import { VideoUploader } from './VideoUploader'

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

export const WithoutImage: StoryObj<typeof VideoUploader> = {
  args: {},
}
