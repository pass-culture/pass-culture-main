// eslint-disable-next-line import/named
import { ComponentStory } from '@storybook/react'
import { Formik } from 'formik'

import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import {
  StockThingEventForm,
  STOCK_THING_EVENT_FORM_DEFAULT_VALUES,
  getValidationSchema,
  IStockThingEventFormValues,
} from '.'

export default {
  title: 'components/StockThingEventForm',
  component: StockThingEventForm,
}

const today = getLocalDepartementDateTimeFromUtc(getToday(), '75')
const tomorrow = getLocalDepartementDateTimeFromUtc(getToday(), '75')
tomorrow.setDate(tomorrow.getDate() + 1)

interface IRenderStockThingEventForm {
  initialValues?: IStockThingEventFormValues
}

const renderStockThingEventForm =
  ({
    initialValues,
  }: IRenderStockThingEventForm): ComponentStory<typeof StockThingEventForm> =>
  args =>
    (
      <Formik
        initialValues={initialValues || STOCK_THING_EVENT_FORM_DEFAULT_VALUES}
        onSubmit={async (values: IStockThingEventFormValues) => {
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
                <StockThingEventForm {...args} />
              </FormLayout.Row>
            </div>
            <SubmitButton onClick={handleSubmit} isLoading={isSubmitting}>
              Valider
            </SubmitButton>
          </form>
        )}
      </Formik>
    )

const Template: ComponentStory<typeof StockThingEventForm> =
  renderStockThingEventForm({})
export const Default = Template.bind({})
Default.args = {
  today,
}

const TemplateWithInitialValues: ComponentStory<typeof StockThingEventForm> =
  renderStockThingEventForm({
    initialValues: {
      eventDatetime: new Date(),
      eventTime: today,
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
