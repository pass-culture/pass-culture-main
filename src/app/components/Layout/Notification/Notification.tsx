import "./Notification.scss"

import React, { forwardRef, useImperativeHandle, useState } from "react"

import { NotificationComponent } from "./NotificationComponent"

export enum NotificationType {
  success = "success",
  error = "error",
}

export class Notification {
  text: string;
  type: NotificationType;

  constructor(type: NotificationType, text: string) {
    this.text = text
    this.type = type
  }
}

export interface NotificationRef {
  notify(notification: Notification): (notification: Notification) => void;
}

export const NotificationWrapper = forwardRef((props, ref) => {
  const [notification, setNotification] = useState<Notification | null>(null)

  useImperativeHandle(ref, () => ({
    notify(newNotification) {
      setNotification(newNotification)
    },
  }))

  return (
    <NotificationComponent
      notification={notification}
      setNotification={setNotification}
    />
  )
})

NotificationWrapper.displayName = "NotificationWrapper"
