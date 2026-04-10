import toast from "@brenoroosevelt/toast";

const baseOptions = {
    position: "top" as const,
    align: "end" as const,
    duration: 5000,
};

export function notifySuccess(message: string): void {
    void toast.success(message, baseOptions);
}

export function notifyInfo(message: string): void {
    void toast.info(message, baseOptions);
}

export function notifyWarning(message: string): void {
    void toast.warning(message, baseOptions);
}

export function notifyError(message: string): void {
    void toast.error(message, { ...baseOptions, duration: 7000 });
}
