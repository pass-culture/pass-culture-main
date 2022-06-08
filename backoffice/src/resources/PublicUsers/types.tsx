import {RaRecord} from "react-admin";


export interface UserManualReview {
    id: string,
    eligibility: "" | "UNDERAGE" | "AGE18",
    reason: string,
    review: "OK" | "KO" | "REDIRECTED_TO_DMS"
}

export enum SubscriptionItemStatus {
    KO = "ko",
    OK = "ko",
    NOT_APPLICABLE = "not-applicable",
    VOID = "void"
}

export interface CheckHistory {
    type: string,
    thirdPartyId: string,
    dateCreated: Date,
    status: "ok" | "void" | "not-applicable" | "ko",
    reason?: string,
    reasonCodes?: string,
    technicalDetails?: object,
    sourceId?: string
}

export interface CheckHistories {
    histories: CheckHistory[]
}