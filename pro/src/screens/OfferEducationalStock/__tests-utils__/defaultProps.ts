import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'

import { IOfferEducationalStockProps } from '../OfferEducationalStock'

import { offerFactory } from './offerFactory'

export const defaultProps: IOfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: offerFactory({}),
  onSubmit: jest.fn(
    (
      offer: GetStockOfferSuccessPayload,
      values: OfferEducationalStockFormValues
    ) => ({ id: 'AA' })
  ),
  mode: Mode.CREATION,
  isShowcaseFeatureEnabled: true,
}
