import { FieldSuccess } from './FieldSuccess'

export default {
  title: 'ui-kit/forms/shared/FieldSuccess',
  component: FieldSuccess,
}

const Template = () => (
  <FieldSuccess name="foo"> field success message </FieldSuccess>
)

export const Default = Template.bind({})
