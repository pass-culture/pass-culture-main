import cn from 'classnames'
import { useEffect, useId, useRef, useState } from 'react'
import { useLocation } from 'react-router'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { PostProAssistantMessageResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { ProAssistantEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Markdown } from '@/components/Markdown/Markdown'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'
import fullCloseIcon from '@/icons/full-close.svg'
import fullInfoIcon from '@/icons/full-info.svg'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import fullRobotIcon from '@/icons/full-robot.svg'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ProAssistant.module.scss'

const MAX_MESSAGE_LENGTH = 500

const SUGGESTIONS = [
  'Comment créer une offre collective ?',
  'Où voir mes remboursements ?',
  'Comment valider une contremarque ?',
  'Comment inviter un collaborateur ?',
]

type ConversationItem =
  | { id: string; role: 'user'; text: string }
  | {
      id: string
      role: 'assistant'
      response: PostProAssistantMessageResponseModel
    }

export const ProAssistant = (): JSX.Element | null => {
  const isProAssistantActive = useActiveFeature('WIP_ENABLE_PRO_ASSISTANT')
  const currentUser = useAppSelector(selectCurrentUser)
  const location = useLocation()

  if (
    !isProAssistantActive ||
    !currentUser ||
    location.pathname.startsWith('/adage-iframe')
  ) {
    return null
  }

  return <ProAssistantWidget />
}

const CulturoAvatar = ({ isLarge = false }: { isLarge?: boolean }) => (
  <span className={cn(styles['avatar'], { [styles['avatar-large']]: isLarge })}>
    <SvgIcon src={fullRobotIcon} alt="" width={isLarge ? '24' : '20'} />
  </span>
)

// Visible name of the assistant, also read by screen readers before each answer
const CulturoAuthor = () => (
  <p className={styles['author']}>
    <CulturoAvatar />
    Culturo
  </p>
)

interface AnswerGroupProps {
  label: string
  isStacked?: boolean
  children: React.ReactNode
}

const AnswerGroup = ({
  label,
  isStacked = false,
  children,
}: AnswerGroupProps) => {
  const labelId = useId()

  return (
    <div className={styles['group']}>
      <p id={labelId} className={styles['group-label']}>
        {label}
      </p>
      <ul
        aria-labelledby={labelId}
        className={
          isStacked ? styles['group-list-stacked'] : styles['group-list']
        }
      >
        {children}
      </ul>
    </div>
  )
}

const ProAssistantWidget = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const offererId = useAppSelector((state) =>
    location.pathname.startsWith('/administration')
      ? (state.user.selectedAdminOfferer?.id ??
        state.user.selectedPartnerVenue?.managingOfferer.id)
      : (state.user.selectedPartnerVenue?.managingOfferer.id ??
        state.user.selectedAdminOfferer?.id)
  )

  const panelId = useId()
  const titleId = useId()
  const [isOpen, setIsOpen] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [items, setItems] = useState<ConversationItem[]>([])
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const toggleButtonRef = useRef<HTMLButtonElement>(null)
  const textAreaRef = useRef<HTMLTextAreaElement>(null)
  const panelBodyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      textAreaRef.current?.focus()
    }
  }, [isOpen])

  // biome-ignore lint/correctness/useExhaustiveDependencies: scroll down when a message is added
  useEffect(() => {
    const panelBody = panelBodyRef.current
    if (panelBody) {
      panelBody.scrollTop = panelBody.scrollHeight
    }
  }, [items.length, isLoading])

  // Icon only, so that it does not hide the action buttons at the bottom of the pages
  const toggleButtonLabel = isOpen ? 'Fermer Culturo' : 'Demander à Culturo'

  const togglePanel = () => {
    if (!isOpen) {
      logEvent(ProAssistantEvents.OPENED_PRO_ASSISTANT)
    }
    setIsOpen(!isOpen)
  }

  const closePanel = () => {
    setIsOpen(false)
    toggleButtonRef.current?.focus()
  }

  const startNewConversation = () => {
    setConversationId(null)
    setItems([])
    setError(null)
    textAreaRef.current?.focus()
  }

  const sendMessage = async (message: string) => {
    const trimmedMessage = message.trim()
    if (!trimmedMessage || isLoading) {
      return
    }
    setError(null)
    setIsLoading(true)
    setItems((previousItems) => [
      ...previousItems,
      { id: crypto.randomUUID(), role: 'user', text: trimmedMessage },
    ])
    setQuestion('')
    // Keyboard users stay in the field to ask the next question
    textAreaRef.current?.focus()
    logEvent(ProAssistantEvents.SENT_PRO_ASSISTANT_MESSAGE, {
      isNewConversation: conversationId === null,
    })

    try {
      const response = await api.postProAssistantMessage({
        body: {
          message: trimmedMessage,
          conversationId,
          offererId: offererId ?? null,
          currentPath: location.pathname,
        },
      })
      setConversationId(response.conversationId)
      setItems((previousItems) => [
        ...previousItems,
        { id: crypto.randomUUID(), role: 'assistant', response },
      ])
    } catch (apiError) {
      setError(
        getHumanReadableApiError(
          apiError,
          'Culturo n’a pas pu répondre. Veuillez réessayer.'
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  // Enter sends the question, Shift + Enter and Option (Alt) + Enter add a line break
  const handleQuestionKeyDown = (
    event: React.KeyboardEvent<HTMLFormElement>
  ) => {
    const textArea = textAreaRef.current
    if (
      !textArea ||
      event.target !== textArea ||
      event.key !== 'Enter' ||
      event.shiftKey ||
      event.nativeEvent.isComposing
    ) {
      return
    }
    event.preventDefault()
    if (event.altKey) {
      // Browsers do not add a line break with Option + Enter: insert it, then notify React
      if (textArea.value.length < MAX_MESSAGE_LENGTH) {
        textArea.setRangeText(
          '\n',
          textArea.selectionStart,
          textArea.selectionEnd,
          'end'
        )
        textArea.dispatchEvent(new Event('input', { bubbles: true }))
      }
      return
    }
    void sendMessage(question)
  }

  return (
    <div className={styles['pro-assistant']}>
      {isOpen && (
        <section
          id={panelId}
          className={styles['panel']}
          aria-labelledby={titleId}
        >
          <header className={styles['panel-header']}>
            <CulturoAvatar isLarge />
            <div className={styles['panel-heading']}>
              <h2 id={titleId} className={styles['panel-title']}>
                Culturo
              </h2>
              <p className={styles['panel-subtitle']}>
                Assistant IA de l’espace partenaire
              </p>
            </div>
            {items.length > 0 && (
              <Button
                variant={ButtonVariant.TERTIARY}
                icon={fullRefreshIcon}
                iconAlt="Nouvelle conversation"
                tooltip="Nouvelle conversation"
                onClick={startNewConversation}
              />
            )}
            <Button
              variant={ButtonVariant.TERTIARY}
              icon={fullCloseIcon}
              iconAlt="Fermer Culturo"
              onClick={closePanel}
            />
          </header>

          <div ref={panelBodyRef} className={styles['panel-body']}>
            <div className={styles['assistant-message']}>
              <div className={styles['answer']}>
                <CulturoAuthor />
                <p className={styles['bubble']}>
                  Bonjour, je suis <strong>Culturo</strong> ! Posez-moi une
                  question sur l’espace partenaire, je vous indique où aller.
                </p>
              </div>
              {items.length === 0 && (
                <AnswerGroup label="Exemples de questions">
                  {SUGGESTIONS.map((suggestion) => (
                    <li key={suggestion}>
                      <Button
                        variant={ButtonVariant.SECONDARY}
                        size={ButtonSize.SMALL}
                        label={suggestion}
                        onClick={() => sendMessage(suggestion)}
                      />
                    </li>
                  ))}
                </AnswerGroup>
              )}
            </div>
            <p className={styles['privacy-notice']}>
              <SvgIcon src={fullInfoIcon} alt="" width="16" />
              Ne saisissez pas de données personnelles (email, téléphone,
              IBAN…).
            </p>

            <div
              className={styles['messages']}
              aria-live="polite"
              aria-busy={isLoading}
            >
              {items.map((item) =>
                item.role === 'user' ? (
                  <p key={item.id} className={styles['user-message']}>
                    <span className={styles['visually-hidden']}>Vous : </span>
                    {item.text}
                  </p>
                ) : (
                  <div key={item.id} className={styles['assistant-message']}>
                    <div className={styles['answer']}>
                      <CulturoAuthor />
                      <p className={styles['bubble']}>
                        <Markdown markdownText={item.response.answer} />
                      </p>
                    </div>
                    {item.response.links.length > 0 && (
                      <AnswerGroup label="Aller à la page">
                        {item.response.links.map((link) => (
                          <li key={link.path}>
                            <Button
                              as="router-link"
                              to={link.path}
                              variant={ButtonVariant.SECONDARY}
                              size={ButtonSize.SMALL}
                              label={link.label}
                              onClick={() =>
                                logEvent(
                                  ProAssistantEvents.CLICKED_PRO_ASSISTANT_LINK,
                                  {
                                    linkPath: link.path,
                                  }
                                )
                              }
                            />
                          </li>
                        ))}
                      </AnswerGroup>
                    )}
                    {item.response.helpArticles.length > 0 && (
                      <AnswerGroup label="Pour aller plus loin" isStacked>
                        {item.response.helpArticles.map((article) => (
                          <li key={article.url}>
                            <Button
                              as="a"
                              to={article.url}
                              opensInNewTab
                              variant={ButtonVariant.TERTIARY}
                              size={ButtonSize.SMALL}
                              label={article.title}
                              onClick={() =>
                                logEvent(
                                  ProAssistantEvents.CLICKED_PRO_ASSISTANT_LINK,
                                  {
                                    linkPath: article.url,
                                  }
                                )
                              }
                            />
                          </li>
                        ))}
                      </AnswerGroup>
                    )}
                  </div>
                )
              )}
              {isLoading && (
                <p className={styles['loading']}>
                  <CulturoAvatar />
                  <span className={styles['loading-dots']} aria-hidden="true">
                    <span className={styles['loading-dot']} />
                    <span className={styles['loading-dot']} />
                    <span className={styles['loading-dot']} />
                  </span>
                  Culturo réfléchit…
                </p>
              )}
            </div>
            {error && (
              <p className={styles['error']} role="alert">
                {error}
              </p>
            )}
          </div>

          <form
            className={styles['form']}
            onSubmit={(event) => {
              event.preventDefault()
              void sendMessage(question)
            }}
            onKeyDown={handleQuestionKeyDown}
          >
            <TextArea
              ref={textAreaRef}
              name="proAssistantQuestion"
              label="Votre question"
              description="Entrée pour envoyer, Maj + Entrée pour aller à la ligne."
              initialRows={2}
              maxLength={MAX_MESSAGE_LENGTH}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <div className={styles['form-actions']}>
              <Button
                type="submit"
                label="Envoyer"
                isLoading={isLoading}
                disabled={!question.trim()}
              />
            </div>
          </form>
        </section>
      )}

      <div className={styles['toggle-button']}>
        <Button
          ref={toggleButtonRef}
          icon={fullRobotIcon}
          iconAlt={toggleButtonLabel}
          tooltip={toggleButtonLabel}
          aria-expanded={isOpen}
          aria-controls={isOpen ? panelId : undefined}
          onClick={togglePanel}
        />
      </div>
    </div>
  )
}
