import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'

import * as useAnalytics from 'app/App/analytics/firebase'
import { IndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import {
  ImageUploaderOffer,
  ImageUploaderOfferProps,
} from '../ImageUploaderOffer'

const mockLogEvent = vi.fn()

const TEST_OFFER_ID = 12

const renderImageUploaderOffer = (props: ImageUploaderOfferProps) => {
  const contextValue = individualOfferContextValuesFactory({
    offer: getIndividualOfferFactory({ id: TEST_OFFER_ID }),
  })

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
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
    </IndividualOfferContext.Provider>,
    {
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
    }
  )
}

describe('ImageUploaderOffer::tracker', () => {
  let props: ImageUploaderOfferProps

  beforeEach(() => {
    props = {
      onImageUpload: vi.fn().mockResolvedValue(undefined),
      onImageDelete: vi.fn().mockResolvedValue(undefined),
    }

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should log add image event on click', async () => {
    renderImageUploaderOffer(props)

    await userEvent.click(screen.getByLabelText('Importez une image'))

    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_ADD_IMAGE, {
      offererId: '1',
      offerId: TEST_OFFER_ID,
      imageType: UploaderModeEnum.OFFER,
      isEdition: false,
      offerType: 'individual',
      imageCreationStage: 'add image',
    })
  })
})
