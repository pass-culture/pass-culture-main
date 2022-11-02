// eslint-disable-next-line import/named
import { ComponentStory } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import {
  StockEventForm,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
  getValidationSchema,
  IStockEventFormValues,
} from '.'

export default {
  title: 'components/StockThingEventForm',
  component: StockEventForm,
}

const today = getLocalDepartementDateTimeFromUtc(getToday(), '75')
const tomorrow = getLocalDepartementDateTimeFromUtc(getToday(), '75')
tomorrow.setDate(tomorrow.getDate() + 1)

interface IRenderStockThingEventForm {
  initialValues?: IStockEventFormValues
}

const renderStockThingEventForm =
  ({
    initialValues,
  }: IRenderStockThingEventForm): ComponentStory<typeof StockEventForm> =>
  args =>
    (
      <Formik
        initialValues={initialValues || STOCK_EVENT_FORM_DEFAULT_VALUES}
        onSubmit={async (values: IStockEventFormValues) => {
          alert(`onSubmit with values: ${JSON.stringify(values)}`)
          return Promise.resolve()
        }}
        validationSchema={getValidationSchema()}
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
                <StockEventForm {...args} />
              </FormLayout.Row>
            </div>
            <SubmitButton onClick={handleSubmit} isLoading={isSubmitting}>
              Valider
            </SubmitButton>
          </form>
        )}
      </Formik>
    )

const Template: ComponentStory<typeof StockEventForm> =
  renderStockThingEventForm({})
export const Default = Template.bind({})
Default.args = {
  today,
}

const TemplateWithInitialValues: ComponentStory<typeof StockEventForm> =
  renderStockThingEventForm({
    initialValues: {
      beginningDate: new Date(),
      beginningTime: today,
      stockId: 'STOCK_ID',
      remainingQuantity: '7',
      bookingsQuantity: '5',
      price: '5',
      bookingLimitDatetime: getLocalDepartementDateTimeFromUtc(
        new Date().toISOString(),
        '75'
      ),
      quantity: '10',
    },
  })

export const WithInitialValues = TemplateWithInitialValues.bind({})
WithInitialValues.args = {
  today,
}

export const Disabled = TemplateWithInitialValues.bind({})
Disabled.args = {
  readOnlyFields: [
    'eventDatetime',
    'eventTime',
    'price',
    'bookingLimitDatetime',
    'quantity',
  ],
  today,
}
