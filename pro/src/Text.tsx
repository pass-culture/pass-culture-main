import styles from './Test.module.scss'

export const Text = () => {
  return (
    <>
      <div className={styles['used-orphan-class']}></div>

      <div>
        <div
          className={styles['partially-used-parent-class--used-child-class']}
        ></div>

        <div>
          <div
            className={
              styles[
                'partially-used-parent-class--partially-used-child-class--used-grandchild-class'
              ]
            }
          ></div>
        </div>
      </div>
    </>
  )
}
