export type Category = {
    id: string;
    proLabel: string;
    isSelectable: boolean;
}

export type SubCategory = {
    id: string;
    categoryId: string;
    matchingType: string;
    proLabel: string;
    appLabel: string;
    searchGroupName: string;
    isEvent: boolean;
    conditionalFields: string[];
    canExpire: boolean;
    canBeDuo: boolean;
    canBeEducational: boolean;
    onlineOfflinePlatform: string;
    isDigitalDeposit: boolean;
    isPhysicalDeposit: boolean;
    reimbursementRule: string;
    isSelectable: boolean;
}
