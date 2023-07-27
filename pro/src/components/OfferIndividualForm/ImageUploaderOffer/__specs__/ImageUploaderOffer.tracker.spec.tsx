import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import {
  OfferIndividualContext,
  OfferIndividualContextValues,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import ImageUploaderOffer, {
  ImageUploaderOfferProps,
} from '../ImageUploaderOffer'

const mockLogEvent = vi.fn()

const renderImageUploaderOffer = (
  props: ImageUploaderOfferProps,
  contextOverride?: Partial<OfferIndividualContextValues>
) => {
  const contextValue: OfferIndividualContextValues = {
    offerId: 12,
    offer: individualOfferFactory({ id: 12 }),
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    shouldTrack: true,
    setShouldTrack: () => {},
    showVenuePopin: {},
    ...contextOverride,
  }

  return renderWithProviders(
    <OfferIndividualContext.Provider value={contextValue}>
      <Formik
        initialValues={{
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
        onSubmit={vi.fn()}
      >
        <Form>
          <ImageUploaderOffer {...props} />
        </Form>
      </Formik>
    </OfferIndividualContext.Provider>
  )
}

describe('ImageUploaderOffer::tracker', () => {
  let props: ImageUploaderOfferProps

  beforeEach(() => {
    props = {
      onImageUpload: vi.fn().mockResolvedValue(undefined),
      onImageDelete: vi.fn().mockResolvedValue(undefined),
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should log add image event on click', async () => {
    renderImageUploaderOffer(props)

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter une image' })
    )

    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_ADD_IMAGE, {
      offerId: 12,
      imageType: UploaderModeEnum.OFFER,
      isEdition: true,
    })
  })
})
