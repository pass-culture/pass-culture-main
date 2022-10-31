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

// TODO: others templates
// const TemplateWithInitialValues
// export const WithInitialValues
// export const Disabled
