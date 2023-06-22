/**
 * Add control over the user registration stepper:
 * - show step content when available
 * - animate progress to active step
 *
 * Macro template for this addon can be found in `src/pcapi/routes/backoffice_v3/templates/components/public_accounts/registration_steps.html`
 */
class PcRegistrationSteps extends PcAddOn {

    static REGISTRATION_STEPS_SELECTOR = '[data-registration-steps-id]'
    static STEPS_SELECTOR = '.steps'
    static STEP_ACTIVE_SELECTOR = 'div.step-active'
    static PROGRESS_BAR_SELECTOR = '.progress-bar'
    static STEP_CONTENT_SELECTOR = '.step-content'
    static STEP_DISABLED_SELECTOR = '.step-disabled'

    state = {}

    get $registrationSteps() {
        return document.querySelectorAll(PcRegistrationSteps.REGISTRATION_STEPS_SELECTOR)
    }

    bindEvents = () => {
        this.$registrationSteps.forEach(($registrationStep) => {
            const { registrationStepsId } = $registrationStep.dataset
            const $steps = this.#getSteps($registrationStep)
            this.state[registrationStepsId] = {
                length: $steps.length,
            }

            $steps.forEach(($step, index) => {
                $step.dataset.registrationStepsId = registrationStepsId
                $step.dataset.stepIndex = index
            })
            EventHandler.on(document, 'click', PcRegistrationSteps.STEPS_SELECTOR, this.#onStepClick)
        })
    }

    unbindEvents = () => {
        EventHandler.off(document, 'click', PcRegistrationSteps.STEPS_SELECTOR, this.#onStepClick)
    }

    #getRegistrationStepFromId(id) {
        return document.querySelector(`${PcRegistrationSteps.REGISTRATION_STEPS_SELECTOR.slice(0, -1)}="${id}"]`)
    }

    #getSteps($registrationStep) {
        return $registrationStep.querySelectorAll(PcRegistrationSteps.STEPS_SELECTOR)
    }

    #getProgressBar($registrationStep) {
        return $registrationStep.querySelector(PcRegistrationSteps.PROGRESS_BAR_SELECTOR)
    }

    #onStepClick = (event) => {
        const disabled = event.target.classList.contains(PcRegistrationSteps.STEP_DISABLED_SELECTOR.slice(1))
        if (disabled) {
            return
        }
        const { registrationStepsId, stepId, stepIndex } = event.target.dataset
        const { length } = this.state[registrationStepsId]
        this.#resetActive(event, stepIndex * (100 / (length - 1)), stepId)
    }

    #resetActive = (event, percent, stepId) => {
        const { registrationStepsId } = event.target.dataset
        const $registrationStep = this.#getRegistrationStepFromId(registrationStepsId)
        const progressBar = this.#getProgressBar($registrationStep)
        progressBar.style.width = `${percent}%`
        progressBar.setAttribute('aria-valuenow', percent)

        $registrationStep.querySelectorAll('.step-active').forEach(($step) => {
            $step.classList.remove('step-active')
        })

        event.target.parentNode.classList.add('step-active')

        this.#hideStepInfos($registrationStep)
        this.#showCurrentStepInfo($registrationStep, stepId)
    }

    #hideStepInfos = ($registrationStep) => {
        $registrationStep.querySelectorAll(PcRegistrationSteps.STEP_CONTENT_SELECTOR).forEach(($stepContent) => {
            $stepContent.classList.remove('d-block')
            $stepContent.classList.add('d-none')
        })
    }

    #showCurrentStepInfo = ($registrationStep, stepId) => {
        const $step = $registrationStep.querySelector(`.${stepId}`)
        if ($step) {
            $step.classList.remove('d-none')
            $step.classList.add('d-block')
        }
    }
}