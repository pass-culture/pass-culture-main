import type { ComponentStory } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import {
  IStockEventFormValues,
  StockEventForm,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
  getValidationSchema as getEventValidationSchema,
} from 'components/StockEventForm'
import {
  StockThingForm,
  IStockThingFormValues,
  getValidationSchema,
  STOCK_THING_FORM_DEFAULT_VALUES,
} from 'components/StockThingForm'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import StockFormRow from './StockFormRow'

export default {
  title: 'components/stocks/StockFormRow',
  component: StockFormRow,
}

const today = getLocalDepartementDateTimeFromUtc(getToday(), '75')

interface IRenderStockFormRow {
  initialValues?: IStockThingFormValues
}
const renderStockFormRow =
  ({
    initialValues,
  }: IRenderStockFormRow): ComponentStory<typeof StockFormRow> =>
  args =>
    (
      <Formik
        initialValues={initialValues || STOCK_THING_FORM_DEFAULT_VALUES}
        onSubmit={async (values: IStockThingFormValues) => {
          alert(`onSubmit with values: ${JSON.stringify(values)}`)
          return Promise.resolve()
        }}
        validationSchema={getValidationSchema()}
        validateOnChange={false}
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
              <StockFormRow {...args} />
            </div>
            <SubmitButton onClick={handleSubmit} isLoading={isSubmitting}>
              Valider
            </SubmitButton>
          </form>
        )}
      </Formik>
    )

interface IRenderStockEventFormRow {
  initialValues?: IStockEventFormValues
}
const renderStockEventFormRow =
  ({
    initialValues,
  }: IRenderStockEventFormRow): ComponentStory<typeof StockFormRow> =>
  args =>
    (
      <Formik
        initialValues={initialValues || STOCK_EVENT_FORM_DEFAULT_VALUES}
        onSubmit={async (values: IStockEventFormValues) => {
          alert(`onSubmit with values: ${JSON.stringify(values)}`)
          return Promise.resolve()
        }}
        validationSchema={getEventValidationSchema()}
        validateOnChange={false}
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
              <StockFormRow {...args} />
            </div>
            <SubmitButton onClick={handleSubmit} isLoading={isSubmitting}>
              Valider
            </SubmitButton>
          </form>
        )}
      </Formik>
    )

const Template: ComponentStory<typeof StockFormRow> = renderStockFormRow({})
const TemplateEvent: ComponentStory<typeof StockFormRow> =
  renderStockEventFormRow({})

const actionsCallBack = (name: string) => () => {
  alert(`Action ${name} have been call`)
}
export const Create = Template.bind({})
Create.args = {
  Form: <StockThingForm today={today} />,
  actions: [
    {
      callback: actionsCallBack('one'),
      label: 'Action one',
      disabled: false,
      Icon: TrashFilledIcon,
    },
    {
      callback: actionsCallBack('two'),
      label: 'Action two',
      disabled: false,
      Icon: TrashFilledIcon,
    },
    {
      callback: actionsCallBack('disabled'),
      label: 'Disabled action',
      disabled: true,
      Icon: TrashFilledIcon,
    },
    {
      callback: actionsCallBack('four'),
      label: 'Action four',
      disabled: false,
      Icon: TrashFilledIcon,
    },
  ],
  actionDisabled: false,
}

const TemplateWithInitialValues: ComponentStory<typeof StockFormRow> =
  renderStockFormRow({
    initialValues: {
      stockId: 'STOCK_ID',
      remainingQuantity: '7',
      bookingsQuantity: '5',
      price: '11',
      bookingLimitDatetime: getLocalDepartementDateTimeFromUtc(
        new Date().toISOString(),
        '75'
      ),
      quantity: '12',
    },
  })

export const Edite = TemplateWithInitialValues.bind({})
Edite.args = {
  ...Create.args,
}

export const WithoutActions = Template.bind({})
WithoutActions.args = {
  Form: <StockThingForm today={today} />,
  actions: [],
  actionDisabled: false,
}

export const CreateEvent = TemplateEvent.bind({})
CreateEvent.args = {
  Form: <StockEventForm today={today} />,
  actions: [
    {
      callback: actionsCallBack('one'),
      label: 'Action one',
      disabled: false,
      Icon: TrashFilledIcon,
    },
    {
      callback: actionsCallBack('two'),
      label: 'Action two',
      disabled: false,
      Icon: TrashFilledIcon,
    },
    {
      callback: actionsCallBack('disabled'),
      label: 'Disabled action',
      disabled: true,
      Icon: TrashFilledIcon,
    },
    {
      callback: actionsCallBack('four'),
      label: 'Action four',
      disabled: false,
      Icon: TrashFilledIcon,
    },
  ],
  actionDisabled: false,
}
