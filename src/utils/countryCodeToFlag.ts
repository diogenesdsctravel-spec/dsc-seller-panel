export function countryCodeToFlag(code: string): string {
    if (!code) return "🇧🇷";
    const upper = code.toUpperCase().trim();
    if (upper.length !== 2) return "🇧🇷";

    return upper
        .split("")
        .map((char) => String.fromCodePoint(127397 + char.charCodeAt(0)))
        .join("");
}
