// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'
import { Banner } from 'ui-kit'

import { UserIdentityForm } from '../'
import { IUserIdentityFormProps } from '../UserIdentityForm'

const patchIdentityAdapterMock = jest.fn()

const renderUserIdentityForm = (props: IUserIdentityFormProps) => {
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser: {
        email: 'test@test.test',
        id: '11',
        isAdmin: false,
        firstName: 'John',
        lastName: 'Do',
      },
    },
  })
  return render(
    <Provider store={store}>
      <UserIdentityForm {...props} />
    </Provider>
  )
}

describe('new_components:UserIdentityForm', () => {
  let props: IUserIdentityFormProps
  beforeEach(() => {
    patchIdentityAdapterMock.mockResolvedValue({})
    props = {
      title: 'What are you?',
      subtitleFormat: () => 'A bird',
      initialValues: {
        firstName: 'FirstName',
        lastName: 'lastName',
      },
      banner: <Banner>Banner test text</Banner>,
      shouldDisplayBanner: false,
      patchIdentityAdapter: patchIdentityAdapterMock,
    }
  })
  it('renders component successfully', () => {
    renderUserIdentityForm(props)
    const element = screen.getByTestId(/test-profile-form/i)
    expect(element).toBeInTheDocument()
  })
  it('should toggle a slider when editing / closing the form', async () => {
    renderUserIdentityForm(props)
    const editButton = screen.getByText('Modifier')
    await userEvent.click(editButton)
    expect(editButton).not.toBeInTheDocument()
    const fields = screen.getAllByRole('textbox')
    expect(fields.length).toEqual(2)
    await userEvent.click(screen.getByText('Annuler'))
    expect(screen.getByText('Modifier')).toBeInTheDocument()
  })
  it('should trigger onSubmit callback when submitting', async () => {
    renderUserIdentityForm(props)
    await userEvent.click(screen.getByText('Modifier'))
    await userEvent.type(screen.getByLabelText('Prénom'), 'Harry')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    await expect(patchIdentityAdapterMock).toHaveBeenCalledTimes(1)
  })
  it('should render a banner when shouldDisplayBanner', async () => {
    props.shouldDisplayBanner = true
    renderUserIdentityForm(props)
    const bannerText = screen.getByText('Banner test text')
    expect(bannerText).toBeInTheDocument()
    await userEvent.click(screen.getByText('Modifier'))
    expect(bannerText).not.toBeInTheDocument()
  })
})
