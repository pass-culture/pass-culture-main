import { Story } from '@storybook/react'
import React from 'react'

import ImageEditor, { IImageEditorProps } from './ImageEditor'
import sampleImage from './sample-image.jpg'

export default {
  title: 'components/ImageEditor',
  component: ImageEditor,
}

const Template: Story<IImageEditorProps> = props => (
  <>
    <ImageEditor {...props} ref={null} />
    <h1>
      Ne pas cliquer sur l'onglet "DOCS" de ce storybook, car il ne fonctionne
      pas.
    </h1>
  </>
)

export const Default = Template.bind({})
Default.args = {
  canvasHeight: 300,
  canvasWidth: 400,
  cropBorderColor: '#FFF',
  cropBorderHeight: 30,
  cropBorderWidth: 40,
  image: sampleImage,
}

export const WithInitialScale = Template.bind({})
WithInitialScale.args = {
  canvasHeight: 300,
  canvasWidth: 400,
  cropBorderColor: '#FFF',
  cropBorderHeight: 30,
  cropBorderWidth: 40,
  image: sampleImage,
  initialScale: 1.5,
}
