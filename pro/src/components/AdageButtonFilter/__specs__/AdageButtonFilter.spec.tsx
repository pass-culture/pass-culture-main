import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import AdageButtonFilter, { AdageButtonFilterProps } from '../AdageButtonFilter'

const renderAdageButtonFilter = ({
  title,
  isActive,
  children,
  disabled,
  itemsLength,
  isOpen,
  setIsOpen,
  handleSubmit,
  formikValues,
  filterName,
}: AdageButtonFilterProps) =>
  renderWithProviders(
    <>
      <AdageButtonFilter
        title={title}
        isActive={isActive}
        children={children}
        disabled={disabled}
        itemsLength={itemsLength}
        isOpen={isOpen}
        setIsOpen={setIsOpen}
        filterName={filterName}
        handleSubmit={handleSubmit}
        formikValues={formikValues}
      />
      <div>Click outside</div>
    </>
  )

describe('AdageButtonFilter', () => {
  const props = {
    title: 'Lieu de l’intervention',
    isActive: false,
    isOpen: true,
    setIsOpen: jest.fn(),
    filterName: 'domains',
    handleSubmit: jest.fn(),
    formikValues: { query: '', domains: [], students: [] },
  }

  it('should render adageButtonFilter', () => {
    renderAdageButtonFilter(props)

    expect(screen.getByText('Lieu de l’intervention')).toBeInTheDocument()
  })

  it('should open filter dialog on click', async () => {
    renderAdageButtonFilter({ ...props, children: 'Test adagebuttonfilter' })

    const filterButton = screen.getByText('Lieu de l’intervention')

    await userEvent.click(filterButton)

    await waitFor(() =>
      expect(screen.getByText('Test adagebuttonfilter')).toBeInTheDocument()
    )
  })

  it('should close dialog when the user focuses outside of the field', async () => {
    renderAdageButtonFilter({ ...props, children: 'Test adagebuttonfilter' })

    const filterButton = screen.getByText('Lieu de l’intervention')
    const outsideDiv = screen.getByText('Click outside')

    await userEvent.click(filterButton)
    await userEvent.click(screen.getByText('Test adagebuttonfilter'))

    await waitFor(() =>
      expect(screen.queryByText('Test adagebuttonfilter')).toBeInTheDocument()
    )

    await userEvent.click(outsideDiv)

    expect(
      screen.queryByRole('dialog', { name: 'Test adagebuttonfilter' })
    ).not.toBeInTheDocument()
  })

  it('should render adageButtonFilter disabled', async () => {
    renderAdageButtonFilter({
      ...props,
      children: <div>Test adagebuttonfilter</div>,
      disabled: true,
    })

    const filterButton = screen.getByRole('button', {
      name: 'Lieu de l’intervention',
    })

    expect(filterButton).toBeDisabled()
  })

  it('should render adageButtonFilter with number of item selected', async () => {
    renderAdageButtonFilter({
      ...props,
      isActive: true,
      children: <div>Test adagebuttonfilter</div>,
      disabled: true,
      itemsLength: 3,
    })

    expect(
      screen.getByRole('button', {
        name: 'Lieu de l’intervention (3)',
      })
    ).toBeInTheDocument()
  })
})
