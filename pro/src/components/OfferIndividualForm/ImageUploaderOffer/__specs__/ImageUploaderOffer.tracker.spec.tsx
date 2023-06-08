import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import ImageUploaderOffer, {
  IImageUploaderOfferProps,
} from '../ImageUploaderOffer'

const mockLogEvent = jest.fn()

const renderImageUploaderVenue = (
  props: IImageUploaderOfferProps,
  contextOverride?: Partial<IOfferIndividualContext>
) => {
  const contextValue: IOfferIndividualContext = {
    offerId: 'OFFER_ID',
    offer: individualOfferFactory({ id: 'OFFER_ID' }),
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
        onSubmit={jest.fn()}
      >
        <Form>
          <ImageUploaderOffer {...props} />
        </Form>
      </Formik>
    </OfferIndividualContext.Provider>
  )
}

describe('ImageUploaderOffer::tracker', () => {
  let props: IImageUploaderOfferProps

  beforeEach(() => {
    props = {
      onImageUpload: jest.fn().mockResolvedValue(undefined),
      onImageDelete: jest.fn().mockResolvedValue(undefined),
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should log add image event on click', async () => {
    renderImageUploaderVenue(props)

    await userEvent.click(screen.getByTestId('add-image-button'))

    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_ADD_IMAGE, {
      offerId: 'OFFER_ID',
      imageType: UploaderModeEnum.OFFER,
    })
  })
})
