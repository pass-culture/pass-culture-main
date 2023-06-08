import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import ImageUploaderVenue from '../ImageUploaderVenue'

const mockLogEvent = jest.fn()

const renderImageUploaderVenue = () =>
  renderWithProviders(
    <Formik
      initialValues={{
        id: 1,
        imageUrl: 'noimage.jpg',
        originalImageUrl: 'noimage.jpg',
        credit: 'John Do',
        cropParams: {
          xCropPercent: 100,
          yCropPercent: 100,
          heightCropPercent: 1,
          widthCropPercent: 1,
        },
      }}
      onSubmit={jest.fn()}
    >
      <Form>
        <ImageUploaderVenue />
      </Form>
    </Formik>
  )

describe('ImageUploaderVenue::tracker', () => {
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should log add image event on click', async () => {
    renderImageUploaderVenue()

    await userEvent.click(screen.getByTestId('add-image-button'))

    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_ADD_IMAGE, {
      venueId: 1,
      imageType: UploaderModeEnum.VENUE,
    })
  })
})
