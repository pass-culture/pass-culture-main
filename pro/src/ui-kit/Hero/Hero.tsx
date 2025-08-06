import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './Hero.module.scss'

/**
 * Props for the Hero component.
 */
interface HeroProps {
  /**
   * The title of the hero section.
   */
  title: string
  /**
   * The text content for the hero section.
   */
  text: string
  /**
   * The label for the link button.
   */
  linkLabel: string
  /**
   * The destination URL for the link button.
   */
  linkTo: string
}

/**
 * The Hero component is used to display a prominent section on a page, typically at the top.
 * It includes a title, subtitle, and a button link for additional actions.
 *
 * ---
 * **Important: Use the `linkTo` prop to provide the URL for the primary action of the hero section.**
 * ---
 *
 * @param {HeroProps} props - The props for the Hero component.
 * @returns {JSX.Element} The rendered Hero component.
 *
 * @example
 * <Hero
 *   title="Welcome to Our Platform"
 *   text="We provide the best solutions for your needs."
 *   linkLabel="Get Started"
 *   linkTo="/get-started"
 * />
 *
 * @accessibility
 * - **Heading Levels**: The title (`h1`) and subtitle (`h2`) provide a clear hierarchy for screen readers.
 * - **Button Label**: Ensure the button label (`linkLabel`) is descriptive to indicate the action it performs.
 */
export const Hero = ({
  title,
  text,
  linkLabel,
  linkTo,
}: HeroProps): JSX.Element => (
  <section className={styles['hero']}>
    <div className={styles['hero-body']}>
      <h1 className={styles['title']}>{title}</h1>
      <h2 className={styles['subtitle']}>{text}</h2>
      <ButtonLink variant={ButtonVariant.PRIMARY} to={linkTo}>
        {linkLabel}
      </ButtonLink>
    </div>
  </section>
)
