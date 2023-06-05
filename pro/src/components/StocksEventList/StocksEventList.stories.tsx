import type { ComponentStory } from '@storybook/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'
import { withRouterDecorator } from 'stories/decorators/withRouter'
import {
  individualStockEventListFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'

import StocksEventList from './StocksEventList'

export default {
  title: 'components/StocksEventList',
  component: StocksEventList,
  decorators: [withRouterDecorator],
}

const Template: ComponentStory<typeof StocksEventList> = () => (
  <div
    style={{
      width: '874px',
      margin: 'auto',
    }}
  >
    <Provider store={configureTestStore({})}>
      <StocksEventList
        stocks={[
          individualStockEventListFactory({ priceCategoryId: 1 }),
          individualStockEventListFactory({ priceCategoryId: 3 }),
          individualStockEventListFactory({ priceCategoryId: 2 }),
          individualStockEventListFactory({ priceCategoryId: 1 }),
          individualStockEventListFactory({ priceCategoryId: 1 }),
          individualStockEventListFactory({ priceCategoryId: 3 }),
          individualStockEventListFactory({ priceCategoryId: 1 }),
          individualStockEventListFactory({ priceCategoryId: 2 }),
          individualStockEventListFactory({ priceCategoryId: 3 }),
          individualStockEventListFactory({ priceCategoryId: 2 }),
          individualStockEventListFactory({ priceCategoryId: 3 }),
          individualStockEventListFactory({ priceCategoryId: 2 }),
          individualStockEventListFactory({ priceCategoryId: 1 }),
          individualStockEventListFactory({ priceCategoryId: 3 }),
          individualStockEventListFactory({ priceCategoryId: 2 }),
          individualStockEventListFactory({ priceCategoryId: 1 }),
        ]}
        priceCategories={[
          priceCategoryFactory({ label: 'Gratuit', price: 0, id: 1 }),
          priceCategoryFactory({
            label: 'Tarif peu cher un peu long didiou',
            price: 12.23,
            id: 2,
          }),
          priceCategoryFactory({
            label: 'Catégorie OR',
            price: 296.98,
            id: 3,
          }),
        ]}
        setStocks={() => {}}
        offerId="AA"
        departmentCode="75"
      />
    </Provider>
  </div>
)

export const Default = Template.bind({})

Default.args = {}
