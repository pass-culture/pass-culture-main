import { DEFAULT_EAC_STOCK_FORM_VALUES, Mode } from 'core/OfferEducational'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import { IOfferEducationalStockProps } from '../OfferEducationalStock'

export const defaultProps: IOfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: collectiveOfferFactory({}),
  onSubmit: jest.fn(),
  mode: Mode.CREATION,
}
