import { DEFAULT_EAC_STOCK_FORM_VALUES, Mode } from 'core/OfferEducational'

import { IOfferEducationalStockProps } from '../OfferEducationalStock'

import { offerFactory } from './offerFactory'

export const defaultProps: IOfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: offerFactory({}),
  onSubmit: jest.fn(),
  mode: Mode.CREATION,
  isShowcaseFeatureEnabled: true,
}
