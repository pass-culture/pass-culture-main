import { yupResolver } from '@hookform/resolvers/yup'
import {
  fireEvent,
  type RenderHookResult,
  renderHook,
  screen,
  waitFor,
} from '@testing-library/react'
import userEvent, { type UserEvent } from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { useForm } from 'react-hook-form'
import * as router from 'react-router'
import {
  createRoutesStub,
  Link,
  type Location,
  type NavigateFunction,
  useLocation,
  useNavigate,
} from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { type InferType, object } from 'yup'

import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'

import { useFormNavigationGuard } from './useFormNavigationGuard'

const EXPECTATIONS = {
  DIALOG_TITLE: 'Des modifications ont été apportées à cette page',
}

const renderNavigationGuardedFakeForm = (initialProps: {
  afterSubmitPath?: string | (() => string)
  isExternallyDirty?: boolean
  resetFormAfterSubmit?: boolean
  onSubmit: () => Promise<boolean>
}) => {
  const fakeFormSchema = object({
    aField: nonEmptyStringOrNull().required('A Field is required.'),
  })

  type FakeFormValues = InferType<typeof fakeFormSchema>

  const FormPage = () => {
    const form = useForm<FakeFormValues>({
      defaultValues: { aField: '' },
      resolver: yupResolver(fakeFormSchema),
    })

    const { navigationGuardedSubmitHandler, navigationGuardDialog } =
      useFormNavigationGuard({
        afterSubmitPath: initialProps.afterSubmitPath,
        form,
        isExternallyDirty: initialProps.isExternallyDirty,
        onSubmit: async () => {
          const canProceed = await initialProps.onSubmit()

          if (initialProps.resetFormAfterSubmit) {
            form.reset(form.getValues())
          }

          return canProceed
        },
      })

    return (
      <>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <input
            aria-label="A Field"
            type="text"
            {...form.register('aField')}
          />
          <span>{form.formState.errors.aField?.message}</span>
          <button type="submit">Sauvegarder</button>
        </form>

        <Link to="/another-page">Go to another page</Link>

        {navigationGuardDialog}
      </>
    )
  }

  return renderHook(
    () => ({
      location: useLocation(),
      navigate: useNavigate(),
    }),
    {
      initialProps,
      wrapper: ({ children }: { children?: ReactNode }) => {
        const ReactRouterStub = createRoutesStub([
          {
            path: '/form-page',
            Component: () => (
              <>
                <FormPage />
                {children}
              </>
            ),
          },
          {
            path: '/another-page',
            Component: () => (
              <>
                <h1>Another Page</h1>
                {children}
              </>
            ),
          },
          {
            path: '/after-submit-page',
            Component: () => (
              <>
                <h1>After Submit Page</h1>
                {children}
              </>
            ),
          },
        ])

        return <ReactRouterStub initialEntries={['/form-page']} />
      },
    }
  )
}

vi.mock('react-router', async () => {
  const actual =
    await vi.importActual<typeof import('react-router')>('react-router')
  return {
    ...actual,
    useBlocker: vi.fn((condition) => actual.useBlocker(condition)),
  }
})

describe('useFormNavigationGuard', () => {
  const onSubmitMock = vi.fn()

  describe('when attempting to navigate to another page', () => {
    it('should not guard when form is clean', async () => {
      const user = userEvent.setup()
      const { result } = renderNavigationGuardedFakeForm({
        afterSubmitPath: '/after-submit-page',
        onSubmit: onSubmitMock,
      })

      expect(result.current.location.pathname).toBe('/form-page')

      await user.click(screen.getByRole('link', { name: 'Go to another page' }))

      expect(result.current.location.pathname).toBe('/another-page')
    })

    it('should guard when `isExternallyDirty` is true even though the RHF form is clean', async () => {
      const user = userEvent.setup()
      const { result } = renderNavigationGuardedFakeForm({
        afterSubmitPath: '/after-submit-page',
        isExternallyDirty: true,
        onSubmit: onSubmitMock,
      })

      expect(result.current.location.pathname).toBe('/form-page')

      await user.click(screen.getByRole('link', { name: 'Go to another page' }))

      expect(result.current.location.pathname).toBe('/form-page')
      expect(
        await screen.findByRole('dialog', { name: EXPECTATIONS.DIALOG_TITLE })
      ).toBeVisible()
    })

    describe('when form is dirty', () => {
      let user: UserEvent
      let result: RenderHookResult<
        {
          location: Location<any>
          navigate: NavigateFunction
        },
        {
          afterSubmitPath?: string | (() => string)
          isExternallyDirty?: boolean
          resetFormAfterSubmit?: boolean
          onSubmit: () => Promise<boolean>
        }
      >

      beforeEach(() => {
        user = userEvent.setup()

        result = renderNavigationGuardedFakeForm({
          afterSubmitPath: '/after-submit-page',
          onSubmit: onSubmitMock,
        })
      })

      describe('without validation errors', () => {
        beforeEach(async () => {
          await user.type(
            await screen.findByRole('textbox', { name: 'A Field' }),
            'new value'
          )

          expect(screen.getByRole('textbox', { name: 'A Field' })).toHaveValue(
            'new value'
          )
        })

        describe('when clicking "Ignorer les modifications"', () => {
          it('should let navigation proceed', async () => {
            await user.click(
              screen.getByRole('link', { name: 'Go to another page' })
            )

            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              await screen.findByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).toBeVisible()

            await user.click(
              screen.getByRole('button', { name: 'Ignorer les modifications' })
            )

            expect(result.result.current.location.pathname).toBe(
              '/another-page'
            )
            expect(
              screen.queryByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).not.toBeInTheDocument()
            expect(onSubmitMock).not.toHaveBeenCalled()
          })
        })

        describe('when clicking "Enregistrer et quitter"', () => {
          it('should block navigation if onSubmit return false', async () => {
            onSubmitMock.mockResolvedValueOnce(false)

            await user.click(
              screen.getByRole('link', { name: 'Go to another page' })
            )

            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              await screen.findByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).toBeVisible()

            await user.click(
              await screen.findByRole('button', {
                name: 'Enregistrer et quitter',
              })
            )

            await waitFor(() => {
              expect(onSubmitMock).toHaveBeenCalledOnce()
            })
            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              screen.queryByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).not.toBeInTheDocument()
          })

          it('should let navigation proceed if onSubmit return true', async () => {
            onSubmitMock.mockResolvedValueOnce(true)

            await user.click(
              screen.getByRole('link', { name: 'Go to another page' })
            )

            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              await screen.findByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).toBeVisible()

            await user.click(
              await screen.findByRole('button', {
                name: 'Enregistrer et quitter',
              })
            )

            await waitFor(() => {
              expect(result.result.current.location.pathname).toBe(
                '/another-page'
              )
            })
            expect(
              screen.queryByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).not.toBeInTheDocument()
            expect(onSubmitMock).toHaveBeenCalledOnce()
          })

          it('should disable the actions while the submission is pending', async () => {
            let resolveOnSubmit: (canProceed: boolean) => void = () => {}
            onSubmitMock.mockImplementationOnce(
              () =>
                new Promise<boolean>((resolve) => {
                  resolveOnSubmit = resolve
                })
            )

            await user.click(
              screen.getByRole('link', { name: 'Go to another page' })
            )

            await user.click(
              await screen.findByRole('button', {
                name: 'Enregistrer et quitter',
              })
            )

            await waitFor(() => {
              expect(
                screen.getByRole('button', { name: 'Enregistrer et quitter' })
              ).toBeDisabled()
            })
            expect(
              screen.getByRole('button', { name: 'Ignorer les modifications' })
            ).toBeDisabled()

            resolveOnSubmit(true)

            await waitFor(() => {
              expect(result.result.current.location.pathname).toBe(
                '/another-page'
              )
            })
            expect(onSubmitMock).toHaveBeenCalledOnce()
          })
        })

        describe('when closing the dialog', () => {
          it('should stay on the current page without submitting', async () => {
            await user.click(
              screen.getByRole('link', { name: 'Go to another page' })
            )

            expect(
              await screen.findByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).toBeVisible()

            const closeButton = screen.getByLabelText(
              'Fermer la boite de dialogue'
            )
            await user.click(closeButton)

            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              screen.queryByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).toBeNull()
            expect(onSubmitMock).not.toHaveBeenCalled()
          })
        })
      })

      describe('with validation errors', () => {
        beforeEach(async () => {
          await user.type(
            await screen.findByRole('textbox', { name: 'A Field' }),
            ' '
          )
        })

        describe('when clicking "Enregistrer et quitter"', () => {
          it('should block navigation', async () => {
            expect(
              screen.getByRole('textbox', { name: 'A Field' })
            ).toHaveValue(' ')

            await user.click(
              screen.getByRole('link', { name: 'Go to another page' })
            )

            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              await screen.findByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).toBeVisible()

            await user.click(
              await screen.findByRole('button', {
                name: 'Enregistrer et quitter',
              })
            )

            expect(result.result.current.location.pathname).toBe('/form-page')
            expect(
              await screen.findByText('A Field is required.')
            ).toBeVisible()
            expect(
              screen.queryByRole('dialog', {
                name: EXPECTATIONS.DIALOG_TITLE,
              })
            ).not.toBeInTheDocument()
            expect(onSubmitMock).not.toHaveBeenCalled()
          })
        })
      })
    })
  })

  describe('when submitting the form directly (without navigating away)', () => {
    const dirtyTheForm = async () => {
      await fireEvent.change(screen.getByLabelText('A Field'), {
        target: { value: 'new value' },
      })
    }

    describe('when onSubmit returns true', () => {
      it('should navigate to the `afterSubmitPath` string', async () => {
        const user = userEvent.setup()
        onSubmitMock.mockResolvedValueOnce(true)

        const { result } = renderNavigationGuardedFakeForm({
          afterSubmitPath: '/after-submit-page',
          onSubmit: onSubmitMock,
        })

        await dirtyTheForm()

        await user.click(screen.getByRole('button', { name: 'Sauvegarder' }))

        await waitFor(() => {
          expect(result.current.location.pathname).toBe('/after-submit-page')
        })
        expect(onSubmitMock).toHaveBeenCalledOnce()
      })

      it('should navigate to the `afterSubmitPath` function result', async () => {
        const user = userEvent.setup()
        onSubmitMock.mockResolvedValueOnce(true)

        const { result } = renderNavigationGuardedFakeForm({
          afterSubmitPath: () => '/after-submit-page',
          onSubmit: onSubmitMock,
        })

        await dirtyTheForm()

        await user.click(screen.getByRole('button', { name: 'Sauvegarder' }))

        await waitFor(() => {
          expect(result.current.location.pathname).toBe('/after-submit-page')
        })
        expect(onSubmitMock).toHaveBeenCalledOnce()
      })

      it('should reset the form when there is no `afterSubmitPath`', async () => {
        const user = userEvent.setup()
        onSubmitMock.mockResolvedValueOnce(true)

        const { result } = renderNavigationGuardedFakeForm({
          onSubmit: onSubmitMock,
        })

        await dirtyTheForm()

        await user.click(screen.getByRole('button', { name: 'Sauvegarder' }))

        await waitFor(() => {
          expect(onSubmitMock).toHaveBeenCalledOnce()
        })
        expect(result.current.location.pathname).toBe('/form-page')

        // The form is no longer dirty, so leaving it must not trigger the guard.
        await user.click(
          screen.getByRole('link', { name: 'Go to another page' })
        )

        expect(result.current.location.pathname).toBe('/another-page')
        expect(
          screen.queryByRole('dialog', {
            name: EXPECTATIONS.DIALOG_TITLE,
          })
        ).toBeNull()
      })
    })

    describe('when onSubmit returns false', () => {
      it('should stay on the current page', async () => {
        const user = userEvent.setup()
        onSubmitMock.mockResolvedValueOnce(false)

        const { result } = renderNavigationGuardedFakeForm({
          afterSubmitPath: '/after-submit-page',
          onSubmit: onSubmitMock,
        })

        await dirtyTheForm()

        await user.click(screen.getByRole('button', { name: 'Sauvegarder' }))

        await waitFor(() => {
          expect(onSubmitMock).toHaveBeenCalledOnce()
        })
        expect(result.current.location.pathname).toBe('/form-page')
        expect(
          screen.queryByRole('dialog', {
            name: EXPECTATIONS.DIALOG_TITLE,
          })
        ).toBeNull()
      })
    })
  })

  describe('when the blocker state becomes stale during async submit', () => {
    it('should fallback to explicit navigate when blocker.proceed throws', async () => {
      const user = userEvent.setup()
      const blocker = {
        location: {
          hash: '#hash',
          pathname: '/another-page',
          search: '?foo=bar',
        },
        proceed: vi.fn(() => {
          throw new Error(
            'Invalid blocker state transition: unblocked -> proceeding'
          )
        }),
        reset: vi.fn(),
        state: 'blocked',
      }

      const useBlockerSpy = vi
        .mocked(router.useBlocker)
        .mockReturnValue(blocker as never)

      onSubmitMock.mockResolvedValueOnce(true)

      const { result } = renderNavigationGuardedFakeForm({
        afterSubmitPath: '/after-submit-page',
        onSubmit: onSubmitMock,
      })

      fireEvent.change(screen.getByLabelText('A Field'), {
        target: { value: 'new value' },
      })

      await user.click(
        await screen.findByRole('button', {
          name: 'Enregistrer et quitter',
        })
      )

      await waitFor(() => {
        expect(onSubmitMock).toHaveBeenCalledOnce()
      })

      expect(blocker.proceed).toHaveBeenCalledOnce()
      expect(blocker.reset).toHaveBeenCalledOnce()
      expect(result.current.location.pathname).toBe('/another-page')
      expect(result.current.location.search).toBe('?foo=bar')
      expect(result.current.location.hash).toBe('#hash')

      useBlockerSpy.mockRestore()
    })
  })
})
