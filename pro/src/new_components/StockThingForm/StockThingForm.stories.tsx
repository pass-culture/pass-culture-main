import type { ComponentStory } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import {
  StockThingForm,
  IStockThingFormValues,
  getValidationSchema,
  STOCK_THING_FORM_DEFAULT_VALUES,
} from '.'

export default {
  title: 'components/StockThingForm',
  component: StockThingForm,
}

const today = getLocalDepartementDateTimeFromUtc(getToday(), '75')

interface IRenderStockThingForm {
  initialValues?: IStockThingFormValues
}
const renderStockThingForm =
  ({
    initialValues,
  }: IRenderStockThingForm): ComponentStory<typeof StockThingForm> =>
  args =>
    (
      <Formik
        initialValues={initialValues || STOCK_THING_FORM_DEFAULT_VALUES}
        onSubmit={async (values: IStockThingFormValues) => {
          alert(`onSubmit with values: ${JSON.stringify(values)}`)
          return Promise.resolve()
        }}
        validationSchema={getValidationSchema(today)}
      >
        {({ handleSubmit, isSubmitting }) => (
          <form onSubmit={handleSubmit}>
            <div
              style={{
                width: '874px',
                margin: 'auto',
                background: '#FAFAFA',
                marginBottom: '24px',
              }}
            >
              <FormLayout.Row inline>
                <StockThingForm {...args} />
              </FormLayout.Row>
            </div>
            <SubmitButton onClick={handleSubmit} isLoading={isSubmitting}>
              Valider
            </SubmitButton>
          </form>
        )}
      </Formik>
    )

const Template: ComponentStory<typeof StockThingForm> = renderStockThingForm({})

export const Default = Template.bind({})
Default.args = {
  today,
}

const TemplateWithInitialValues: ComponentStory<typeof StockThingForm> =
  renderStockThingForm({
    initialValues: {
      stockId: 'STOCK_ID',
      remainingQuantity: '7',
      bookingsQuantity: '5',
      price: '10',
      bookingLimitDatetime: getLocalDepartementDateTimeFromUtc(
        '2022-10-06T21:59:59z',
        '75'
      ),
      quantity: '12',
    },
  })

export const WithInitialValues = TemplateWithInitialValues.bind({})
WithInitialValues.args = {
  today,
}
export const Disabled = TemplateWithInitialValues.bind({})
Disabled.args = {
  readOnlyFields: ['price', 'bookingLimitDatetime', 'quantity'],
  today,
}
