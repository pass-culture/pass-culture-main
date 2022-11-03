import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import SiretOrCommentFields, {
  SiretOrCommentInterface,
} from '../SiretOrCommentFields'

const renderSiretOrCommentFields = (
  props?: Partial<SiretOrCommentInterface>
) => {
  const store = configureTestStore()
  const siren = '000000000'
  const siretLabel = 'Siret field'
  const updateIsSiretValued = jest.fn()
  const defaultProps = {
    isCreatedEntity: true,
    siren: siren,
    siretLabel: siretLabel,
    readOnly: false,
    updateIsSiretValued: updateIsSiretValued,
  }
  render(
    <Provider store={store}>
      <Form initialValues={{}} name="venue" onSubmit={() => {}}>
        {() => <SiretOrCommentFields {...{ ...defaultProps, ...props }} />}
      </Form>
    </Provider>
  )
}

describe('components | SiretOrCommentFields', () => {
  it('should display siret field by default', async () => {
    renderSiretOrCommentFields()
    await screen.findByRole('button', {
      name: 'Je veux créer un lieu avec SIRET',
    })

    const siretField = screen.getByLabelText('Siret field*')
    expect(siretField).toBeInTheDocument()
    expect(siretField).toBeRequired()
    const commentField = screen.queryByText('Commentaire du lieu sans SIRET : ')
    expect(commentField).not.toBeInTheDocument()
  })

  it('should display comment field when toggle is clicked', async () => {
    renderSiretOrCommentFields()

    const toggle = await screen.findByRole('button', {
      name: 'Je veux créer un lieu avec SIRET',
    })
    await userEvent.click(toggle)
    const siretField = screen.queryByText('Siret field')
    expect(siretField).not.toBeInTheDocument()
    const commentField = screen.getByLabelText(
      'Commentaire du lieu sans SIRET : ',
      {
        exact: false,
      }
    )
    expect(commentField).toBeInTheDocument()
    expect(commentField).toBeRequired()
  })

  it('should display toggle disabled', async () => {
    renderSiretOrCommentFields({ isToggleDisabled: true })

    const toggle = await screen.findByRole('button', {
      name: 'Je veux créer un lieu avec SIRET',
    })
    expect(toggle).toBeDisabled()
  })
})
